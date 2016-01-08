# -*- coding: utf-8 -*-
import logging
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from gtpros.models import Trabajador, Proyecto, Rol, Resumen, Actividad
from gtpros.forms import RolForm, ResumenForm, InformeForm
from _collections import defaultdict
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

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
    trabajador = Trabajador.objects.get(user__username=request.user.username)
    rol = Rol.objects.get(proyecto__id=pk, trabajador=trabajador)
    request.session['rol'] = rol.tipo_rol
    return render(request, 'gtpros/calendar.html', {})

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
        
    return render(request, 'gtpros/workers.html', {'form': form, 'roles': dict(roles)})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def new_event(request, pk):
    return render(request, 'gtpros/new_event.html', {})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def new_report(request, pk):
    user = request.user
    actividades = Actividad.objects.filter(rol__proyecto__id=pk, rol__trabajador__user=user)
    
    if request.POST:
        form = InformeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('new_report', pk)
            
    else:
        form = InformeForm()

    return render(request, 'gtpros/new_report.html', {'form': form, 'actividades': actividades})

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
            
    return render(request, 'gtpros/project_summary.html', {'form': form, 'resumen': resumen})
