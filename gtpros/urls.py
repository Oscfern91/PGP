# -*- encoding: utf-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
               
    url(r'^$', views.index, name='index'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/$', views.calendar, name='project'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/cargos/$', views.cargos, name='cargos'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/importar/$', views.importar, name='importar'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/delete_worker/(?P<worker>[0-9]+)/$', views.delete_worker, name='delete_worker'),
    
    url(r'^project/(?P<id_proyecto>[0-9]+)/calendarization/$', views.calendarization, name='calendarization'),
    
    url(r'^project/(?P<id_proyecto>[0-9]+)/roles/$', views.roles, name='roles'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/role/(?P<role>[0-9]+)/$', views.roles, name='role_edit'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/activity/(?P<event>[0-9]+)/new_role/$', views.roles, name='role_add'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/roles/ready/(?P<ready_error>[0,1])/$', views.roles, name='roles_ready_error'),
    
    url(r'^project/(?P<id_proyecto>[0-9]+)/ready/$', views.ready, name='ready'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/events/$', views.events, name='events'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/event_detail/(?P<event_id>[0-9]+)/$', views.event_detail, name='event_detail'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/reports/$', views.reports, name='reports'),
    
    
    url(r'^project/(?P<id_proyecto>[0-9]+)/new_report$', views.new_report, name='new_report'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/validate_report$', views.validate_report, name='validate_report'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/validate_event$', views.validate_event, name='validate_event'),
    url(r'^project/(?P<id_proyecto>[0-9]+)/summary$', views.summary, name='summary'),
    
]