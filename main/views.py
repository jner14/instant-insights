from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.clickjacking import xframe_options_exempt
from django.core.mail import send_mail
from .forms import *
# from django.utils import timezone


@xframe_options_exempt
def survey(request):
    return render(request, 'main/survey.html', {})


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