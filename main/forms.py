from django import forms
from .models import Survey, SurveyResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.safestring import mark_safe
from django.contrib.sites.models import Site


class GetCompanyForm(forms.Form):
    company = forms.CharField(max_length=100)


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    team_or_company = forms.CharField(max_length=100, required=False)
    survey_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ('survey_name', "team_or_company", 'first_name', 'last_name', 'email', 'password1', 'password2')

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


class AddSurveyForm(forms.Form):
    survey_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Survey
        fields = ('survey_name',)


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()


class Question1Form(forms.Form):
    CHOICES = [('MGR', 'Yes'), ('ASSOC', 'No')]
    question = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)


class Question2Form(forms.Form):
    CHOICES = [('a', mark_safe("<img class='radioicons' src='http://%s/static/insight/img/risk_a.jpg' alt='High Risk' title='High Risk'>" % Site.objects.get_current().domain)),
               ('b', mark_safe("<img class='radioicons' src='http://%s/static/insight/img/risk_b.jpg' alt='Medium Risk' title='Medium Risk'>" % Site.objects.get_current().domain)),
               ('c', mark_safe("<img class='radioicons' src='http://%s/static/insight/img/risk_c.jpg' alt='Low Risk' title='Low Risk'>" % Site.objects.get_current().domain)),
               ('d', mark_safe("<img class='radioicons' src='http://%s/static/insight/img/risk_d.jpg' alt='No Risk' title='No Risk'>" % Site.objects.get_current().domain))]
    question = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)


class Question3Form(forms.Form):
    CHOICES = [('a', mark_safe("<img class='radioicons' src='http://%s/static/insight/img/support_a.jpg' alt='Supported' title='Supported'>" % Site.objects.get_current().domain)),
               ('b', mark_safe("<img class='radioicons' src='http://%s/static/insight/img/support_b.jpg' alt='Injured' title='Injured'>" % Site.objects.get_current().domain)),
               ('c', mark_safe("<img class='radioicons' src='http://%s/static/insight/img/support_c.jpg' alt='Booted' title='Booted'>" % Site.objects.get_current().domain))]
    question = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
