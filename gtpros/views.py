# -*- coding: utf-8 -*-
from _collections import defaultdict
import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from gtpros.forms import RolForm, ResumenForm, InformeForm, ActividadForm, \
    HitoForm
from gtpros.models import Trabajador, Proyecto, Rol, Resumen, Actividad, Informe,\
    Hito, Evento
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def index(request):
    
    try:
        
        trabajador = Trabajador.objects.get(user__username=request.user.username)
        proyectos = Proyecto.objects.filter(rol__trabajador=trabajador).values('id', 'nombre', 'descripcion', 'activo')
        
        logger.debug('Proyectos de ' + trabajador.user.username + ':')
        logger.debug(proyectos)
        
        request.session['listaProyectos'] = list(proyectos)
        
        if 'rol' in request.session:
            del request.session['rol']
        return render(request, 'gtpros/index.html', {})
    
    except Trabajador.DoesNotExist:
        
        logout(request)
        return redirect('index')

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def calendar(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    trabajador = Trabajador.objects.get(user__username=request.user.username)
    rol = Rol.objects.get(proyecto__id=pk, trabajador=trabajador)
    request.session['rol'] = rol.tipo_rol
    
    if rol.tipo_rol == Rol.JEFE_PROYECTO:
        actividades_temp = list(Actividad.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'rol__trabajador__user__username'))
        hitos_temp = list(Hito.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha'))
    else:
        actividades_temp = list(Actividad.objects.filter(proyecto=proyecto, rol=rol).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'rol__trabajador__user__username'))
        hitos_temp = list(Hito.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha'))
        
    actividades = json.dumps(actividades_temp, default=date_handler)
    hitos = json.dumps(hitos_temp, default=date_handler)
    
    return render(request, 'gtpros/calendar.html', {'proyecto': proyecto, 'actividades': actividades, 'hitos': hitos, })

# Fixes data serialization errors
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def workers(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    roles_temp = Rol.objects.filter(proyecto=proyecto)\
        .order_by('tipo_rol')
    roles = defaultdict(list)
    for rol in roles_temp:
        key = rol.get_tipo_rol_display()
        roles[key].append(rol)
            
    if request.POST:
        form = RolForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('workers', pk)
    else:
        form = RolForm(initial={'proyecto': proyecto})
        
    return render(request, 'gtpros/workers.html', {'proyecto': proyecto, 'form': form, 'roles': dict(roles)})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def delete_worker(request, pk, rol):
    
    Rol.objects.get(pk=rol).delete()
    
    return redirect('workers', pk)

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def new_event(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    type_event = request.GET.get('type', '')
    
    if(request.POST):
        post = request.POST.copy()
        if 'type' in post:
            tipo = post['type']
            if tipo == 'A':
                form = ActividadForm(request.POST)
            else:
                form = HitoForm(request.POST)
                
            if form.is_valid():
                form.save()
                return redirect('project', pk)
    else:
        if type_event == 'A':
            form = ActividadForm(proyecto=proyecto)
        else:
            form = HitoForm(initial={'proyecto': proyecto})
    
    return render(request, 'gtpros/new_event.html', {'proyecto': proyecto, 'form':form, 'tipo': type_event})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def new_report(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    user = request.user
    actividades = Actividad.objects.filter(rol__proyecto__id=pk, rol__trabajador__user=user)
    
    if request.POST:
        form = InformeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('new_report', pk)
            
    else:
        form = InformeForm()

    return render(request, 'gtpros/new_report.html', {'proyecto': proyecto, 'form': form, 'actividades': actividades})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def reports(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    if request.session['rol'] == Rol.JEFE_PROYECTO:
        informes = Informe.objects.filter(actividad__proyecto=proyecto)
    else:
        informes = Informe.objects.filter(actividad__proyecto=proyecto, actividad__rol__trabajador__user=request.user)
    
    return render(request, 'gtpros/reports.html', {'proyecto': proyecto, 'informes': informes, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def validate_report(request, pk):
    
    informeId = request.POST['informe']
    informe = Informe.objects.get(pk=informeId)
    
    aceptado = request.POST['validacion']
    if aceptado == "0":
        informe.aceptado = True
    else:
        informe.aceptado = False
    informe.save()
    
    return redirect('reports', pk)

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def events(request, pk, type):
    proyecto = Proyecto.objects.get(pk=pk)
    
    if type == 'A':
        eventos = Actividad.objects.filter(proyecto=proyecto)
        next = 'gtpros/activities.html'
    else:
        eventos = Hito.objects.filter(proyecto=proyecto)
        next = 'gtpros/boundary_posts.html'
    
    return render(request, next, {'proyecto': proyecto, 'eventos': eventos, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def validate_event(request, pk):
    
    if 'actividad' in request.POST:
        id = request.POST['actividad']
        type = 'A'
        evento = Actividad.objects.get(pk=id)
    else:
        id = request.POST['hito']
        type = 'H'
        evento = Hito.objects.get(pk=id)
    
    aceptado = request.POST['validacion']
    if aceptado == "0":
        evento.cerrado = False
    else:
        evento.cerrado = True
        
    evento.save()
    
    return redirect('events', pk, type)

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def summary(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    try:
        resumen = Resumen.objects.get(proyecto=proyecto)
    except Resumen.DoesNotExist:
        resumen = None
    
    if request.POST:
        form = ResumenForm(request.POST, instance=resumen)
        if form.is_valid():
            form.save()
            return redirect('summary', pk)
            
    else:
        if resumen:
            form = ResumenForm(instance=resumen)
        else:
            form = ResumenForm(initial={'proyecto': proyecto})
            
    return render(request, 'gtpros/project_summary.html', {'proyecto': proyecto, 'form': form, 'resumen': resumen})

def actividad_detalle(request):
    id = request.GET.get('id', '')
    evento = Actividad.objects.get(pk=id)
    
    return render(request, 'gtpros/event_detail.html', {'evento': evento, 'tipo': 'A'})

def hito_detalle(request):
    id = request.GET.get('id', '')
    evento = Hito.objects.get(pk=id)
    
    return render(request, 'gtpros/event_detail.html', {'evento': evento, 'tipo': 'H'})
