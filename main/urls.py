from django.conf.urls import include, url
from django.views.generic import TemplateView
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # url(r'^', include('django.contrib.auth.urls')),
    url(r'^$', views.new_survey_user, name='new_survey_user'),
    url(r'^manage_surveys$', views.manage_surveys, name='manage_surveys'),
    url(r'^close_survey/(?P<pk>[a-f0-9-]+)/$', views.close_survey, name='close_survey'),
    url(r'^open_survey/(?P<pk>[a-f0-9-]+)/$', views.open_survey, name='open_survey'),
    url(r'^get_link/(?P<pk>[a-f0-9-]+)/$', views.get_link, name='get_link'),
    url(r'^take_survey/(?P<survey_pk>[a-f0-9-]+)/(?P<response_pk>[a-f0-9-]+)/(?P<q_num>\d+)/$', views.take_survey,
        name='take_survey'),
    url(r'^submission_received$', views.submission_received, name='submission_received'),
    url(r'^survey_is_closed$', views.survey_is_closed, name='survey_is_closed'),
    url(r'^report_sent$', views.report_sent, name='report_sent'),
    url(r'^report_not_sent$', views.report_not_sent, name='report_not_sent'),
    # url(r'^$', TemplateView.as_view(template_name='insight/home.html')),
]
