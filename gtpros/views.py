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
from datetime import datetime
from django.utils import timezone

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
        
        if 'jefe' in request.session:
            del request.session['jefe']
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
            logger.debug("OK")
            proyecto.estado = Proyecto.ASIGNACION
            proyecto.save()
            return redirect('roles', id_proyecto)
    else:
        form = ProjectForm(instance=proyecto)
    
    return render(request, 'gtpros/calendarization.html', {'proyecto': proyecto, 'form': form, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def roles(request, id_proyecto, role=None, ready_error=False):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    roles_temp = Rol.objects.filter(evento__proyecto=proyecto).order_by('evento')
    roles = defaultdict(list)
    
    for rol in roles_temp:
        key = rol.evento
        roles[key].append(rol)
    
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
                    return redirect('roles_add', id_proyecto, rol)
            else:
                logger.debug("DELETE")
                rol_to_edit.delete()
                return redirect('roles', id_proyecto)
        else:
            form = RolForm(instance=rol_to_edit)
            
        rol_options = {Rol.ANALISTA : rol_2,
                   Rol.DISENADOR: rol_3,
                   Rol.ANALISTA_PROG: rol_3,
                   Rol.RESPONSABLE_PRUEBAS: rol_3,
                   Rol.PROGRAMADOR: rol_4,
                   Rol.PROBADOR: rol_4,
               } 
        
        form.fields["trabajador"].queryset = rol_options[rol.tipo_rol](proyecto)
    else:
        form = None
        
    if role == False:
        logger.debug("Error getting Ready...")
        ready_error = True

    return render(request, 'gtpros/roles.html', {'proyecto': proyecto, 'form': form, 'roles': dict(roles), 'ready_error': ready_error})

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
    roles = Rol.objects.filter(evento__proyecto=id_proyecto, trabajador=None)
    if roles.count() > 0:
        return redirect('roles_ready_error', id_proyecto, 1)
    
    logger.debug("Project Ready!!")
    proyecto.estado = Proyecto.PREPARADO
    checkProject(proyecto)
    proyecto.save()
    
    return redirect('events', id_proyecto)

def checkProject(proyecto):
    
    if proyecto.estado == Proyecto.PREPARADO:
        fechaProyecto = proyecto.fecha_inicio.astimezone(timezone.utc).replace(tzinfo=None)
        logger.debug("Fecha del proyecto:")
        logger.debug(fechaProyecto)
        
        if fechaProyecto <= datetime.now():
            proyecto.estado = Proyecto.INICIADO
            proyecto.save()

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def events(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    details_link = False
    
    if request.session['jefe']:
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
    
    if request.session['jefe']:
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
def validate_event(request, id_proyecto):
    
    id = request.POST['actividad']
    evento = Evento.objects.get(pk=id)
    
    aceptado = request.POST['validacion']
    if aceptado == "0":
        evento.cerrado = False
    else:
        evento.cerrado = True
        
    evento.save()
    
    return redirect('events', id_proyecto, )

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
    request.session['jefe'] = cargo.es_jefe
    
    if cargo.es_jefe:
        eventos_temp = list(Evento.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'rol__trabajador__user__username'))
    else:
        eventos_temp = list(Evento.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'rol__trabajador__user__username'))
         
    eventos = json.dumps(eventos_temp, default=date_handler)
    
    return render(request, 'gtpros/calendar.html', {'proyecto': proyecto, 'eventos': eventos, })

# Fixes data serialization errors
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj