from django.shortcuts import render, get_object_or_404, redirect
from .forms import ContactForm, GetCompanyForm, NewUserForm, Question1Form, Question2Form, Question3Form
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from .models import Survey, SurveyResponse
from django.contrib.auth import authenticate, login as login_user, logout as logout_user
import logging


logger = logging.getLogger(__name__)


def survey_home(request):
    if request.user.is_authenticated():
        return redirect(manage_surveys)
    if request.method == 'POST':
        compForm = GetCompanyForm(request.POST)
        if compForm.is_valid():
            request.session['company'] = compForm.cleaned_data['company']
            return redirect(new_survey_user)
    else:
        compForm = GetCompanyForm()
    return render(request, 'main/survey_home.html', {'compForm': compForm})


def new_survey_user(request):
    if 'company' not in request.session.keys():
        return redirect(survey_home)
    elif request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            # Create new user and authenticate them
            newUser = form.save(commit=False)
            newUser.username = form.cleaned_data['email']
            newUser.save()
            login_user(request, authenticate(request=request,
                                             username=form.cleaned_data['email'],
                                             password=form.cleaned_data['password1']))
            # Create new survey and send email with links
            newSurvey = Survey.objects.create(requester=newUser, company=request.session['company'])
            newSurvey.send_link()
            return redirect(manage_surveys)
    else:
        form = NewUserForm()
    return render(request, 'main/new_survey_user.html', {'form': form})


def manage_surveys(request):
    if request.user.is_anonymous():
        return redirect(login)
    surveys = [(survey, len(SurveyResponse.objects.filter(survey_id=survey.pk, submitted=True)))
               for survey in Survey.objects.filter(requester=request.user)]
    return render(request, 'main/manage_surveys.html', {'surveys': surveys})


def get_link(request, pk):
    if request.user.is_authenticated():
        survey = get_object_or_404(Survey, pk=pk)
        survey.send_link(request.get_host())
        return redirect(manage_surveys)
    return redirect(login)


def close_survey(request, pk):
    if request.user.is_authenticated():
        survey = get_object_or_404(Survey, requester=request.user, pk=pk)
        survey.close()
        survey.send_report()
        return redirect(manage_surveys)
    return redirect(login)


def open_survey(request, pk):
    if request.user.is_authenticated():
        survey = Survey.objects.filter(requester=request.user, pk=pk)
        if survey.exists():
            survey[0].open()
        return redirect(manage_surveys)
    return redirect(login)


def login(request):
    if request.user.is_authenticated():
        return redirect('manage_surveys')
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            login_user(request, authenticate(request=request,
                                             username=form.cleaned_data['username'],
                                             password=form.cleaned_data['password']))
            return redirect(manage_surveys)
    else:
        form = AuthenticationForm()
    return render(request, 'main/../../templates/login.html', {'form': form})


def logout(request):
    logout_user(request)
    return render(request, 'main/../../templates/logout.html', {})


def take_survey(request, survey_pk, response_pk, q_num):
    survey = get_object_or_404(Survey, pk=survey_pk)

    if survey.closed:
        return redirect(survey_is_closed)

    if response_pk != '-1':
        surveyResponse = get_object_or_404(SurveyResponse, pk=response_pk)
    else:
        surveyResponse = SurveyResponse()
        surveyResponse.survey_id = survey_pk
        surveyResponse.save()
        return redirect(take_survey, survey_pk=survey_pk, response_pk=surveyResponse.pk, q_num=1)

    if surveyResponse.submitted:
        return redirect(submission_received)

    if request.method == 'POST':
        if q_num == '1':
            form = Question1Form(data=request.POST)
            if form.is_valid():
                surveyResponse.question_1 = form.cleaned_data["question"]
                surveyResponse.save()
                return redirect(take_survey, survey_pk=survey_pk, response_pk=response_pk, q_num='2')
        elif q_num == '2':
            form = Question2Form(data=request.POST)
            if form.is_valid():
                surveyResponse.question_2 = form.cleaned_data["question"]
                surveyResponse.save()
                return redirect(take_survey, survey_pk=survey_pk, response_pk=response_pk, q_num='3')
        elif q_num == '3':
            form = Question3Form(data=request.POST)
            if form.is_valid():
                surveyResponse.question_3 = form.cleaned_data["question"]
                surveyResponse.submitted = True
                surveyResponse.save()
                return redirect(submission_received)

    if q_num == '3':
        return render(request, 'main/take_survey_q3.html', {'form': Question3Form()})
    elif q_num == '2':
        return render(request, 'main/take_survey_q2.html', {'form': Question2Form()})
    else:  # q_num == '1'
        return render(request, 'main/take_survey_q1.html', {'form': Question1Form()})


def submission_received(request):
    return render(request, 'main/submission_received.html', {})


def survey_is_closed(request):
    return render(request, 'main/survey_is_closed.html', {})
