from django import forms
from .models import Survey, SurveyResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class GetCompanyForm(forms.Form):
    company = forms.CharField(max_length=100)


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(pk=self.instance.pk).filter(username=email).exists():
            raise forms.ValidationError(u'Email "%s" is already in use.' % email)
        return email

    def clean_first_name(self):
        if self.cleaned_data["first_name"].strip() == '':
            raise forms.ValidationError("First name is required.")
        return self.cleaned_data["first_name"]

    def clean_last_name(self):
        if self.cleaned_data["last_name"].strip() == '':
            raise forms.ValidationError("Last name is required.")
        return self.cleaned_data["last_name"]


class ResponseForm(forms.ModelForm):

    class Meta:
        model = SurveyResponse
        fields = ('question_1', 'question_2', 'question_3', 'question_4', 'question_5')


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()
