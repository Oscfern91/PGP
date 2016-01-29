# -*- encoding: utf-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
               
    url(r'^$', views.index, name='index'),
    url(r'^project/(?P<pk>[0-9]+)/$', views.calendar, name='project'),
    url(r'^project/(?P<pk>[0-9]+)/cargos$', views.cargos, name='cargos'),
    url(r'^project/(?P<pk>[0-9]+)/importar', views.importar, name='importar'),
    url(r'^project/(?P<pk>[0-9]+)/delete_worker/(?P<worker>[0-9]+)/$', views.delete_worker, name='delete_worker'),
    url(r'^project/(?P<pk>[0-9]+)/roles/$', views.roles, name='roles'),
    url(r'^project/(?P<pk>[0-9]+)/roles/(?P<role>[0-9]+)/$', views.roles, name='roles_add'),
    url(r'^project/(?P<pk>[0-9]+)/actividades/$', views.actividades, name='actividades'),
    
    url(r'^project/(?P<pk>[0-9]+)/new_report$', views.new_report, name='new_report'),
    url(r'^project/(?P<pk>[0-9]+)/reports$', views.reports, name='reports'),
    url(r'^project/(?P<pk>[0-9]+)/validate_report$', views.validate_report, name='validate_report'),
    url(r'^project/(?P<pk>[0-9]+)/events/(?P<type>[A,H])/$', views.events, name='events'),
    url(r'^project/(?P<pk>[0-9]+)/validate_event$', views.validate_event, name='validate_event'),
    url(r'^project/(?P<pk>[0-9]+)/summary$', views.summary, name='summary'),
    url(r'^actividad_detalle$', views.actividad_detalle, name='actividad_detalle'),
    url(r'^hito_detalle$', views.hito_detalle, name='hito_detalle'),
]