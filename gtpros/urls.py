# -*- encoding: utf-8 -*-
from django.conf.urls import include, url

from . import views


urlpatterns = [
               
    url(r'^$', views.index, name='index'),
    url(r'^project/(?P<pk>[0-9]+)/$', views.calendar, name='project'),
    url(r'^project/(?P<pk>[0-9]+)/workers$', views.workers, name='workers'),
    url(r'^project/(?P<pk>[0-9]+)/delete_worker/(?P<rol>[0-9]+)/$', views.delete_worker, name='delete_worker'),
    url(r'^project/(?P<pk>[0-9]+)/new_event$', views.new_event, name='new_event'),
    url(r'^project/(?P<pk>[0-9]+)/new_report$', views.new_report, name='new_report'),
    url(r'^project/(?P<pk>[0-9]+)/reports$', views.reports, name='reports'),
    url(r'^project/(?P<pk>[0-9]+)/validate_report$', views.validate_report, name='validate_report'),
    url(r'^project/(?P<pk>[0-9]+)/events/(?P<type>[A,H])/$', views.events, name='events'),
    url(r'^project/(?P<pk>[0-9]+)/validate_event$', views.validate_event, name='validate_event'),
    url(r'^project/(?P<pk>[0-9]+)/summary$', views.summary, name='summary'),
    url(r'^event_detail$', views.event_detail, name='event_detail'),
]