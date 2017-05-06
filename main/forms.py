from django import forms
from .models import Survey, SurveyResponse


class CreateSurveyForm(forms.ModelForm):

    class Meta:
        model = Survey
        fields = ('company',)


class ResponseForm(forms.ModelForm):

    class Meta:
        model = SurveyResponse
        fields = ('question_1', 'question_2', 'question_3', 'question_4', 'question_5')


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()
