# coding=utf-8
from time import sleep
from django.db import models
from django.template.loader import render_to_string
# from django.utils import timezone
import uuid
from django.core.mail import send_mail, EmailMessage
# from django.utils.html import strip_tags
from .survey_maker import SurveyReportMaker
import pdfkit
import logging
import os
from .score_innovation import get_rating
from django.core.mail import EmailMultiAlternatives



MIN_RESPONSES = 1
MAX_REPORT_ATTEMPTS = 10
logger = logging.getLogger('django')


class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey('auth.User')
    survey_name = models.CharField(max_length=100, default="NA")
    group_name = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    def close(self):
        self.closed = True
        self.save()

    def open(self):
        self.closed = False
        self.save()

    def send_link(self, domain):
        # content = render_to_string('main/email_survey_link.html', {'group_name': self.group_name,
        #                                                            'survey_pk': self.pk,
        #                                                            'domain': domain})
        # return self.requester.email_user("Here is your I3™ Survey Link from The Innovation Company", content)
        text_content = "Text Content Placeholder"
        html_content = render_to_string('main/email_survey_link.html', {'group_name': self.group_name,
                                                                        'survey_pk': self.pk,
                                                                        'domain': domain})
        message = EmailMultiAlternatives(subject="Here is your I3™ Survey Link from The Innovation Company",
                                         body=text_content,
                                         to=(self.requester.email,))
        message.attach_alternative(html_content, "text/html")
        message.send()

    def send_report(self):
        result = False
        reportName = 'I3 Assessment Report - %s.pdf' % self.group_name
        responses = [[r.question_1, r.question_2, r.question_3]
                     for r in SurveyResponse.objects.filter(survey=self.id, submitted=True)]
        requesterName = "%s %s" % (self.requester.first_name, self.requester.last_name)

        if len(responses) >= MIN_RESPONSES:
            rating, score = get_rating(responses)
            for i in range(MAX_REPORT_ATTEMPTS):
                try:
                    srMaker = SurveyReportMaker(responses, requesterName, rating)
                    srMaker.make_plots()
                    htmlReport = srMaker.make_html_page(os.path.join(os.getcwd(), "static/insight/img/innovation_company_logo.png"))
                    pdf = srMaker.write_to_pdf(htmlReport,
                                               config=pdfkit.configuration(wkhtmltopdf="../.local/bin/wkhtmltox/bin/wkhtmltopdf"))
                    text_content = render_to_string('main/email_report_body.html', {'name': self.requester.first_name})
                    message = EmailMessage(subject="Your I3™ Assessment Report from The Innovation Company",
                                           body=text_content,
                                           to=(self.requester.email,))
                    message.attach(reportName, pdf, 'application/pdf')
                    message.send()
                    # Send email to survey@survey.innovationiseasy.com notifying of report generation, including a copy
                    message.subject = 'A report has been emailed to {} {}'.format(self.requester.first_name, self.requester.last_name)
                    message.to = ['survey@survey.innovationiseasy.com']
                    message.from_email = 'noreply@survey.innovationiseasy.com'
                    message.send()
                    result = True
                    break
                except Exception as e:
                    logger.error("FAILED TO CREATE REPORT: %s" % e)
                    if i >= MAX_REPORT_ATTEMPTS - 1:
                        send_mail(subject="FAILED TO CREATE REPORT %s TIMES" % MAX_REPORT_ATTEMPTS,
                                  message="There was an issue trying to create a report:\n\n%s" % e,
                                  from_email='noreply@survey.innovationiseasy.com',
                                  recipient_list=["survey@survey.innovationiseasy.com"])
                    else:
                        sleep((i + 1) * 120)
        return result

    def __str__(self):
        return str(self.id)


class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey)
    submitted = models.BooleanField(default=False)
    question_1 = models.CharField(max_length=10)
    question_2 = models.CharField(max_length=1)
    question_3 = models.CharField(max_length=1)
