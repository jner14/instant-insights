from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
import uuid
from django.core.mail import send_mail, EmailMessage
from django.utils.html import strip_tags
from .survey_maker import SurveyReportMaker
import pdfkit
import logging
import os


logger = logging.getLogger('django')


class Survey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester = models.ForeignKey('auth.User')
    company = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)

    def close(self):
        self.closed = True
        self.save()

    def open(self):
        self.closed = False
        self.save()

    def send_link(self, domain):
        content = render_to_string('main/email_survey_link.html', {'survey_pk': self.pk, 'domain': domain})
        return self.requester.email_user("Here is your survey link!", content)

    def send_report(self):
        reportName = 'I3 Assessment Report - %s.pdf' % self.company
        responses = [[r.question_1, r.question_2, r.question_3]
                     for r in SurveyResponse.objects.filter(survey=self.id, submitted=True)]
        requesterName = "%s %s" % (self.requester.first_name, self.requester.last_name)
        rating = "placeholder rating"
        # i = 0
        # while i < 5:
        #     try:
        srMaker = SurveyReportMaker(responses, requesterName, rating)
        srMaker.make_plots()
        htmlReport = srMaker.make_html_page(os.path.join(os.getcwd(), "static/insight/img/innovation_company_logo.png"))
        pdf = srMaker.write_to_pdf(htmlReport,
                                   # config=pdfkit.configuration(wkhtmltopdf="C:/Program Files/bin/wkhtmltopdf/bin/wkhtmltopdf.exe"))
                                   config=pdfkit.configuration(wkhtmltopdf="../.local/bin/wkhtmltox/bin/wkhtmltopdf"))
        content = render_to_string('main/email_report_body.html', {'name': self.requester.first_name})
        message = EmailMessage(subject ="Your I3 Assessment Report - The Innovation Company",
                               body = content,
                               to = (self.requester.email,))
        message.attach(reportName, pdf, 'application/pdf')
        message.send()
        message.subject = 'A report has been emailed to {} {}'.format(self.requester.first_name, self.requester.last_name)
        message.to = ['survey@innovationiseasy.com']
        message.from_email = 'no_reply@innovationiseasy.com'
        message.send()

            #     break
            # except Exception as e:
            #     logger.error("Failed to create and send report: %s" % e)
            #     i += 1

    def __str__(self):
        return str(self.id)


class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey)
    submitted = models.BooleanField(default=False)
    question_1 = models.CharField(max_length=10)
    question_2 = models.CharField(max_length=1)
    question_3 = models.CharField(max_length=1)
