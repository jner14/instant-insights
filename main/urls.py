from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # url(r'^', include('django.contrib.auth.urls')),
    url(r'^$', views.survey_home, name='survey_home'),
    url(r'^survey_new_user$', views.survey_new_user, name='survey_new_user'),
    url(r'^survey_manage$', views.survey_manage, name='survey_manage'),
    url(r'^close_survey/(?P<pk>\d+)/$', views.close_survey, name='close_survey'),
    url(r'^open_survey/(?P<pk>\d+)/$', views.open_survey, name='open_survey'),
    url(r'^mail$', views.mail, name='mail'),
    # url(r'^$', TemplateView.as_view(template_name='insight/home.html')),

]
