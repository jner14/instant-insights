from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
import uuid
from django.core.mail import send_mail
from django.utils.html import strip_tags


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
        pass

    def __str__(self):
        return str(self.id)


class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(Survey)
    submitted = models.BooleanField(default=False)
    question_1 = models.CharField(max_length=10)
    question_2 = models.CharField(max_length=1)
    question_3 = models.CharField(max_length=1)
