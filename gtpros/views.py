# -*- coding: utf-8 -*-
from _collections import defaultdict
import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from gtpros.forms import InformeForm, CargoForm, UploadFileForm, RolForm,\
    ProjectForm
from gtpros.models import Trabajador, Proyecto, Rol, Resumen, Informe, Evento, \
    Cargo, Predecesor
import json
from datetime import date
import datetime
import math

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def index(request):
    
    try:
        
        trabajador = Trabajador.objects.get(user=request.user)
        proyectos = Proyecto.objects.filter(cargo__trabajador=trabajador)
        
        logger.debug('Proyectos de ' + trabajador.user.username + ':')
        logger.debug(proyectos)
        
        request.session['listaProyectos'] = proyectos
        
        if 'es_jefe' in request.session:
            del request.session['es_jefe']
        return render(request, 'gtpros/index.html', {})
    
    except Trabajador.DoesNotExist:
        
        logout(request)
        return redirect('index')

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def cargos(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    cargos_temp = Cargo.objects.filter(proyecto=proyecto)
    trabajadores = []
    for cargo in cargos_temp:
        if cargo.es_jefe:
            jefe = cargo.trabajador
        else:
            trabajadores.append(cargo.trabajador)
            
    if request.POST:
        form = CargoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            form.save()
            return redirect('cargos', id_proyecto)
    else:
        form = CargoForm(proyecto=proyecto)
        
    return render(request, 'gtpros/workers.html', {'proyecto': proyecto, 'form': form, 'jefe': jefe, 'trabajadores': trabajadores})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def delete_worker(request, id_proyecto, worker):
    
    Cargo.objects.get(proyecto=id_proyecto, trabajador__pk=worker).delete()
    
    return redirect('cargos', id_proyecto)

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def importar(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            procesar_archivo(proyecto, request.FILES['file'])
            
            proyecto.estado = Proyecto.CALENDARIZACION
            proyecto.save()
            
            return redirect('calendarization', id_proyecto)
    else:
        form = UploadFileForm()
    
    return render(request, 'gtpros/import.html', {'proyecto': proyecto, 'form': form, })

def procesar_archivo(proyecto, data):

    deserialized_data = json.load(data)
    
    listaPredecesores = []
    
    for actividad in deserialized_data["actividades"]:
        actividad_id = actividad["id"]
        nom = actividad["nombre"]
        desc = actividad["descripcion"]
        dur = actividad["duracion"]
        rol = actividad["rol"]
        modelActividad = Evento(id_evento=actividad_id, proyecto=proyecto, nombre=nom, descripcion=desc, duracion=dur, tipo_rol=rol)
        modelActividad.save()
        for predecesor in actividad["predecesores"]:
            evento_previo = Evento.objects.get(id_evento=predecesor["id"], proyecto=proyecto)
            modelPredecesor = Predecesor(evento=modelActividad, evento_anterior=evento_previo)
            listaPredecesores.append(modelPredecesor)
    
    for hito in deserialized_data["hitos"]:
        hito_id = hito["id"]
        nom = hito["nombre"]
        desc = hito["descripcion"]
        modelHito = Evento(id_evento=hito_id, proyecto=proyecto, nombre=nom, descripcion=desc)
        modelHito.save()
        for predecesor in actividad["predecesores"]:
            evento_previo = Evento.objects.get(id_evento=predecesor["id"], proyecto=proyecto)
            modelPredecesor = Predecesor(evento=modelHito, evento_anterior=evento_previo)
            listaPredecesores.append(modelPredecesor)
            
    for predecesor in listaPredecesores:
        predecesor.save()
            
    data.close()

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def calendarization(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    if request.POST:
        form = ProjectForm(request.POST, instance=proyecto)
        if form.is_valid():
            proyecto.estado = Proyecto.ASIGNACION
            proyecto.save()
            return redirect('roles', id_proyecto)
    else:
        form = ProjectForm(instance=proyecto)
    
    return render(request, 'gtpros/calendarization.html', {'proyecto': proyecto, 'form': form, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def roles(request, id_proyecto, role=None, event=None, ready_error=False):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    actividades = Evento.objects.filter(proyecto=proyecto).exclude(duracion=0)
    roles = defaultdict(list)
    
    for actividad in actividades:
        key = actividad
        roles_temp = Rol.objects.filter(evento=actividad)
        roles[key].extend(roles_temp)
    
    if role:
        rol_to_edit = Rol.objects.get(pk=role)
        if request.POST:
            form = RolForm(request.POST, instance=rol_to_edit)
            
            save = request.POST['save']
            if save != '0':
                logger.debug("SAVE")
                if form.is_valid():
                    form.save()
                    return redirect('roles', id_proyecto)
            else:
                logger.debug("DELETE")
                rol_to_edit.delete()
                return redirect('roles', id_proyecto)
        else:
            form = RolForm(instance=rol_to_edit)
            
    else:
        if event:
            event_of_role = Evento.objects.get(pk=event)
            if request.POST:
                form = RolForm(request.POST)
                
                save = request.POST['save']
                if save != '0':
                    logger.debug("SAVE")
                    if form.is_valid():
                        form.save()
                        return redirect('roles', id_proyecto)
                else:
                    logger.debug("DELETE")
                    rol_to_edit.delete()
                    return redirect('roles', id_proyecto)
            else:
                form = RolForm(evento=event_of_role)
                
        else:
            form = None
        
    if role == False:
        logger.debug("Error getting Ready...")
        ready_error = True

    return render(request, 'gtpros/roles.html', {'proyecto': proyecto, 'form': form, 'actividades': actividades, 'roles': dict(roles), 'ready_error': ready_error})

def rol_2(proyecto):
    return get_worker_by_category(proyecto, 2) 
def rol_3(proyecto):
    return get_worker_by_category(proyecto, 3)
def rol_4(proyecto):
    return get_worker_by_category(proyecto, 4)

def get_worker_by_category(proy, cat):
    jefe = Trabajador.objects.get(cargo__proyecto=proy, cargo__es_jefe=True)
    trabajadores = Trabajador.objects.filter(categoria__lte=cat, cargo__proyecto=proy).exclude(pk=jefe.pk)
    
    return trabajadores

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def ready(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    # Remove roles without assigned workers, and activities without roles
    actividades = Evento.objects.filter(proyecto=proyecto).exclude(duracion=0)
    for actividad in actividades:
        roles = Rol.objects.filter(evento=actividad)
        if roles.count() == 0:
            return redirect('roles_ready_error', id_proyecto, 1)
    
    logger.debug("Project Ready!!")
    proyecto.estado = Proyecto.PREPARADO
    checkProject(proyecto)
    proyecto.save()
    
    setEventDates(proyecto)
    
    return redirect('events', id_proyecto)

# Comprobar fecha inicio del proyecto
def checkProject(proyecto):
    
    if proyecto.estado == Proyecto.PREPARADO:
        fechaProyecto = proyecto.fecha_inicio
        logger.debug("Fecha del proyecto:")
        logger.debug(fechaProyecto)
        
        if fechaProyecto <= date.today():
            proyecto.estado = Proyecto.INICIADO
            proyecto.save()

# Asignar fechas a los eventos
def setEventDates(proyecto):
    
    eventos = Evento.objects.filter(proyecto=proyecto)
    
    for evento in eventos:
        predecesores = Predecesor.objects.filter(evento_anterior=evento.pk)
        if predecesores.count() == 0:
            setDate(evento)
    
def setDate(evento):
    
    logger.debug("Set date:")
    logger.debug(evento.nombre)
    predecesores = Predecesor.objects.filter(evento=evento.pk)
    if predecesores.count() == 0:
        evento.fecha_inicio = evento.proyecto.fecha_inicio
    else:
        for predecesor in predecesores:
            evento_anterior = predecesor.evento_anterior
            setDate(evento_anterior)
            fin_pred = evento_anterior.fecha_fin
            logger.debug("date preecesor:")
            logger.debug(fin_pred)
            if not evento.fecha_inicio or fin_pred > evento.fecha_inicio:
                if fin_pred.weekday() == 4:
                    evento.fecha_inicio = fin_pred + datetime.timedelta(days=3)
                else:
                    evento.fecha_inicio = fin_pred + datetime.timedelta(days=1)
                
    calcularFechaFin(evento)
    evento.save()
        
def calcularFechaFin(evento):
    
    num_roles = Rol.objects.filter(evento=evento).count()
    
    semanas = evento.duracion / (num_roles * 40)
    horas_sueltas = evento.duracion % (num_roles * 40)
    dias_sueltos = math.ceil(horas_sueltas / 8.0)
    dias = 0
    
    dia = evento.fecha_inicio
    while dia.weekday() < 5 and dias_sueltos > 0:
        dia = dia + datetime.timedelta(days=1)
        dias = dias + 1
        dias_sueltos = dias_sueltos - 1
    if dias_sueltos > 0:
        dias + dias_sueltos + 2
    
    dias = dias + semanas * 7
    evento.fecha_fin = evento.fecha_inicio + datetime.timedelta(days=dias)

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def events(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    details_link = False
    
    if not 'es_jefe' in request.session:
        return redirect('index')
    
    if request.session['es_jefe']:
        eventos = Evento.objects.filter(proyecto=proyecto)
    else:
        eventos = Evento.objects.filter(proyecto=proyecto, rol__trabajador__user=request.user)
    
    checkProject(proyecto)
    
    if proyecto.estado == Proyecto.INICIADO:
        details_link = True
        
    return render(request, 'gtpros/events.html', {'proyecto': proyecto, 'eventos': eventos, 'details_link': details_link, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def reports(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    if request.session['es_jefe']:
        informes = Informe.objects.filter(evento__proyecto=proyecto)
    else:
        informes = Informe.objects.filter(evento__proyecto=proyecto, evento__rol__trabajador__user=request.user)
    
    return render(request, 'gtpros/reports.html', {'proyecto': proyecto, 'informes': informes, })

def event_detail(request, id_proyecto, event_id):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    evento = Evento.objects.get(pk=event_id)
    
    if evento.duracion == 0:
        tipo = 'H'
    else:
        tipo = 'A'
        
    roles_temp = Rol.objects.filter(evento=evento)
    roles = defaultdict(list)
    
    for rol in roles_temp:
        key = rol.get_tipo_rol_display()
        roles[key].append(rol)
    
    return render(request, 'gtpros/event_detail.html', {'proyecto': proyecto, 'evento': evento, 'tipo': tipo, 'roles': dict(roles), })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def validate_event(request, id_proyecto, event_id):
    
    evento = Evento.objects.get(pk=event_id)
    
    evento.cerrado = True
    evento.fecha_fin = date.today()
    evento.save()
    
#     Recalcular fechas eventos aqui
    
    return redirect('events', id_proyecto, )


@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def new_report(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    user = request.user
    actividades = Evento.objects.filter(rol__trabajador__user=user)
    
    if request.POST:
        form = InformeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('new_report', id_proyecto)
            
    else:
        form = InformeForm()

    return render(request, 'gtpros/new_report.html', {'proyecto': proyecto, 'form': form, 'actividades': actividades})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def validate_report(request, id_proyecto):
    
    informeId = request.POST['informe']
    informe = Informe.objects.get(pk=informeId)
    
    aceptado = request.POST['validacion']
    if aceptado == "0":
        informe.aceptado = True
    else:
        informe.aceptado = False
    informe.save()
    
    return redirect('reports', id_proyecto)

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def summary(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    try:
        resumen = Resumen.objects.get(proyecto=proyecto)
    except Resumen.DoesNotExist:
        resumen = None
            
    return render(request, 'gtpros/project_summary.html', {'proyecto': proyecto, 'resumen': resumen})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def calendar(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    checkProject(proyecto)
    
    trabajador = Trabajador.objects.get(user__username=request.user.username)
    cargo = Cargo.objects.get(proyecto__id=id_proyecto, trabajador=trabajador)
    request.session['es_jefe'] = cargo.es_jefe
    
    if cargo.es_jefe:
        eventos_temp = list(Evento.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'rol__trabajador__user__username'))
    else:
        eventos_temp = list(Evento.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'rol__trabajador__user__username'))
         
    eventos = json.dumps(eventos_temp, default=date_handler)
    
    return render(request, 'gtpros/calendar.html', {'proyecto': proyecto, 'eventos': eventos, })

# Fixes data serialization errors
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj