from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.mail import send_mail
from .forms import ContactForm, GetCompanyForm, ResponseForm, NewUserForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Survey
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


@xframe_options_exempt
def survey_home(request):
    if request.user.is_authenticated():
        return redirect('manage_surveys')
    if request.method == 'POST':
        compForm = GetCompanyForm(request.POST)
        if compForm.is_valid():
            request.session['company'] = compForm.cleaned_data['company']
            return redirect('survey_new_user')
    else:
        compForm = GetCompanyForm()

    return render(request, 'main/survey_home.html', {'compForm': compForm})


@xframe_options_exempt
def survey_new_user(request):
    if 'company' not in request.session.keys():
        return redirect(survey_home)
    elif request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            newUser = form.save(commit=False)
            newUser.username = form.cleaned_data['email']
            newUser.save()
            login(request, authenticate(request=request,
                                        username=form.cleaned_data['email'],
                                        password=form.cleaned_data['password1']))
            newSurvey = Survey.objects.create(requester=newUser, company=request.session['company'])
            return redirect('manage_surveys')
    else:
        form = NewUserForm()

    return render(request, 'main/survey_new_user.html', {'form': form})


@xframe_options_exempt
def manage_surveys(request):
    if request.user.is_anonymous():
        return redirect('survey_home')
    return render(request, 'main/manage_surveys.html', {'surveys': Survey.objects.filter(requester=request.user)})


def close_survey(request, pk):
    if request.user.is_authenticated():
        survey = Survey.objects.filter(requester=request.user, pk=pk)
        if survey.exists():
            survey[0].close()
        return redirect(manage_surveys)
    return redirect(survey_home)


def open_survey(request, pk):
    if request.user.is_authenticated():
        survey = Survey.objects.filter(requester=request.user, pk=pk)
        if survey.exists():
            survey[0].open()
        return redirect(manage_surveys)
    return redirect(survey_home)


def mail(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']

            recipients = ['r.jason.robinson12@gmail.com']

            send_mail(subject, message, sender, recipients)
            return redirect('/thanks/')
    else:
        form = ContactForm()

    return render(request, 'main/mail.html', {'form': form})