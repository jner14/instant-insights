from django.db import models
from django.utils import timezone


class Survey(models.Model):
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

    def __str__(self):
        return str(self.id)


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey)
    question_1 = models.CharField(max_length=1)
    question_2 = models.CharField(max_length=1)
    question_3 = models.CharField(max_length=1)
    question_4 = models.CharField(max_length=1)
    question_5 = models.CharField(max_length=1)
