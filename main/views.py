from django.shortcuts import render, get_object_or_404, redirect
from .forms import ContactForm, GetCompanyForm, ResponseForm, NewUserForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import Survey
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
import logging


logger = logging.getLogger(__name__)


def survey_home(request):
    if request.user.is_authenticated():
        return redirect('survey_manage')
    if request.method == 'POST':
        compForm = GetCompanyForm(request.POST)
        if compForm.is_valid():
            request.session['company'] = compForm.cleaned_data['company']
            return redirect('survey_new_user')
    else:
        compForm = GetCompanyForm()
    return render(request, 'main/survey_home.html', {'compForm': compForm})


def survey_new_user(request):
    if 'company' not in request.session.keys():
        return redirect(survey_home)
    elif request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            newUser = form.save(commit=False)
            newUser.username = form.cleaned_data['email']
            newUser.save()
            login_user(request, authenticate(request=request,
                                        username=form.cleaned_data['email'],
                                        password=form.cleaned_data['password1']))
            newSurvey = Survey.objects.create(requester=newUser, company=request.session['company'])
            return redirect(survey_manage)
    else:
        form = NewUserForm()
    return render(request, 'main/survey_new_user.html', {'form': form})


def survey_manage(request):
    if request.user.is_anonymous():
        return redirect('survey_home')
    return render(request, 'main/survey_manage.html', {'surveys': Survey.objects.filter(requester=request.user)})


def close_survey(request, pk):
    if request.user.is_authenticated():
        survey = Survey.objects.filter(requester=request.user, pk=pk)
        if survey.exists():
            survey[0].close()
        return redirect(survey_manage)
    return redirect(survey_home)


def open_survey(request, pk):
    if request.user.is_authenticated():
        survey = Survey.objects.filter(requester=request.user, pk=pk)
        if survey.exists():
            survey[0].open()
        return redirect(survey_manage)
    return redirect(survey_home)


def login(request):
    if request.user.is_authenticated():
        return redirect('survey_manage')
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            login_user(request, authenticate(request=request,
                                             username=form.cleaned_data['username'],
                                             password=form.cleaned_data['password']))
            return redirect(survey_manage)
    else:
        form = AuthenticationForm()
    return render(request, 'main/../../templates/login.html', {'form': form})


def logout(request):
    logout_user(request)
    return render(request, 'main/../../templates/logout.html', {})
