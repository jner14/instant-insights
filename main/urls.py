from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^survey$', views.survey_home, name='survey_home'),
    url(r'^survey_new_user$', views.survey_new_user, name='survey_new_user'),
    url(r'^manage_surveys$', views.manage_surveys, name='manage_surveys'),
    url(r'^close_survey/(?P<pk>\d+)/$', views.close_survey, name='close_survey'),
    url(r'^open_survey/(?P<pk>\d+)/$', views.open_survey, name='open_survey'),
    url(r'^mail$', views.mail, name='mail'),
    url(r'^$', TemplateView.as_view(template_name='home.html')),
]
