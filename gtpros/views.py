# -*- coding: utf-8 -*-
from _collections import defaultdict
import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from gtpros.forms import InformeForm, CargoForm, UploadFileForm, RolForm,\
    ProjectForm
from gtpros.models import Trabajador, Proyecto, Rol, Resumen, Informe, Evento, \
    Cargo, Predecesor, TipoRol
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
        proyectos = Proyecto.objects.filter(cargo__trabajador=trabajador).exclude(estado=Proyecto.FINALIZADO)
        
        request.session['listaProyectos'] = proyectos
        
        if 'es_jefe' in request.session:
            del request.session['es_jefe']
        return render(request, 'gtpros/index.html', {})
    
    except Trabajador.DoesNotExist:
        
        logout(request)
        return redirect('index')
    
@login_required
@user_passes_test(lambda u: not u.is_superuser)
def project(request, id_proyecto):
    
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    checkProject(proyecto)
    
    trabajador = Trabajador.objects.get(user__username=request.user.username)
    cargo = Cargo.objects.get(proyecto__id=id_proyecto, trabajador=trabajador)
    
    if 'es_jefe' in request.session:
            del request.session['es_jefe']
    request.session['es_jefe'] = cargo.es_jefe
    
    if cargo.es_jefe:
        if proyecto.estado == Proyecto.NUEVO:
            return redirect('cargos', id_proyecto)
        if proyecto.estado == Proyecto.CALENDARIZACION:
            return redirect('calendarization', id_proyecto)
        if proyecto.estado == Proyecto.ASIGNACION:
            return redirect('roles', id_proyecto)
        if proyecto.estado == Proyecto.FINALIZADO:
            return redirect('project_summary', id_proyecto)
     
    return redirect('calendar', id_proyecto)

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
    
    for actividad in deserialized_data["actividades"]:
        actividad_id = actividad["id"]
        nom = actividad["nombre"]
        desc = actividad["descripcion"]
        dur = actividad["duracion"]
        rol = actividad["rol"]
        tipo_rol = TipoRol.objects.get(siglas=rol)
        modelActividad = Evento(id_evento=actividad_id, proyecto=proyecto, nombre=nom, descripcion=desc, duracion=dur, tipo_rol=tipo_rol)
        modelActividad.save()
    
    for hito in deserialized_data["hitos"]:
        hito_id = hito["id"]
        nom = hito["nombre"]
        desc = hito["descripcion"]
        modelHito = Evento(id_evento=hito_id, proyecto=proyecto, nombre=nom, descripcion=desc)
        modelHito.save()
            
    for actividad in deserialized_data["actividades"]:
        for predecesor in actividad["predecesores"]:
            evento_previo = Evento.objects.get(id_evento=predecesor["id"], proyecto=proyecto)
            modelPredecesor = Predecesor(evento=modelActividad, evento_anterior=evento_previo)
            modelPredecesor.save()
    for hito in deserialized_data["hitos"]:
        for predecesor in hito["predecesores"]:
            evento_previo = Evento.objects.get(id_evento=predecesor["id"], proyecto=proyecto)
            modelPredecesor = Predecesor(evento=modelHito, evento_anterior=evento_previo)
            modelPredecesor.save()
            
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
    
    actividades = Evento.objects.filter(proyecto=proyecto).exclude(duracion=0).order_by('id_evento')
    roles = defaultdict(list)
    
    for actividad in actividades:
        key = actividad
        roles_temp = Rol.objects.filter(evento=actividad)
        roles[key].extend(roles_temp)
    
    if role:
        new = False
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
            form = RolForm(instance=rol_to_edit, evento=rol_to_edit.evento)
            
    else:
        new = True
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

    return render(request, 'gtpros/roles.html', {'proyecto': proyecto, 'new': new, 'form': form, 'actividades': actividades, 'roles': dict(roles), 'ready_error': ready_error})

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
        fechaIni = proyecto.fecha_inicio
        logger.debug("Fecha de inicio del proyecto:")
        logger.debug(fechaIni)
        
        if fechaIni <= date.today():
            proyecto.estado = Proyecto.INICIADO
            proyecto.save()
    
    if proyecto.estado == Proyecto.INICIADO:
        fechaFin = proyecto.fecha_fin
        logger.debug("Fecha de inicio del proyecto:")
        logger.debug(fechaFin)
        
@login_required
@user_passes_test(lambda u: not u.is_superuser)
def events(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    details_link = False
    
    if not 'es_jefe' in request.session:
        return redirect('index')
    
    if request.session['es_jefe']:
        eventos = Evento.objects.filter(proyecto=proyecto).order_by('fecha_inicio')
    else:
        eventos = Evento.objects.filter(proyecto=proyecto, rol__trabajador__user=request.user).order_by('fecha_inicio')
    
    checkProject(proyecto)
    
    if proyecto.estado == Proyecto.INICIADO:
        details_link = True
        
    return render(request, 'gtpros/events.html', {'proyecto': proyecto, 'eventos': eventos, 'details_link': details_link, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def reports(request, id_proyecto, id_informe=None):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    form = None
    informeValid = None
    
    if request.session['es_jefe']:
        informes = Informe.objects.filter(rol__evento__proyecto=proyecto, fecha__lte=date.today(), enviado=True).exclude(aceptado=True)
        
        if id_informe:
            informeValid = Informe.objects.get(pk=id_informe)
        
    else:
        informes = Informe.objects.filter(rol__evento__proyecto=proyecto, fecha__lte=date.today(), rol__trabajador__user=request.user).exclude(enviado=True)
    
        if id_informe:
            informe = Informe.objects.get(pk=id_informe)
            
            if request.POST:
                form = InformeForm(request.POST, instance=informe)
                if form.is_valid():
                    formValid = form.save(commit=False)
                    formValid.enviado = True
                    formValid.fecha = date.today()
                    formValid.save()
                    return redirect('reports', id_proyecto)
            else:
                form = InformeForm(instance=informe)
    
    return render(request, 'gtpros/reports.html', {'proyecto': proyecto, 'informes': informes, 'form': form, 'informeValid': informeValid})

def report_popup(request, id_proyecto, report_id):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    informe = Informe.objects.get(pk=report_id)
    
    return render(request, 'gtpros/report_popup.html', {'proyecto': proyecto, 'informe': informe })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def validate_report(request, id_proyecto, id_informe):
    
    informe = Informe.objects.get(pk=id_informe)
    
    aceptado = request.POST['validacion']
    if aceptado == "0":
        informe.aceptado = True
    else:
        informe.aceptado = False
        informe.enviado = False
    
    informe.save()
    
    return redirect('reports', id_proyecto)

@login_required
@user_passes_test(lambda u: not u.is_superuser)
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
        key = rol.tipo_rol.nombre
        roles[key].append(rol)
    
    return render(request, 'gtpros/event_detail.html', {'proyecto': proyecto, 'evento': evento, 'tipo': tipo, 'roles': dict(roles), })

def event_popup(request, id_proyecto, event_id):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    evento = Evento.objects.get(pk=event_id)
    
    if evento.duracion == 0:
        tipo = 'H'
    else:
        tipo = 'A'
        
    roles_temp = Rol.objects.filter(evento=evento)
    roles = defaultdict(list)
    
    for rol in roles_temp:
        key = rol.tipo_rol.nombre
        roles[key].append(rol)
    
    return render(request, 'gtpros/event_popup.html', {'proyecto': proyecto, 'evento': evento, 'tipo': tipo, 'roles': dict(roles), })

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def validate_events(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    details_link = False
    
    if not 'es_jefe' in request.session:
        return redirect('index')
    
    eventos = Evento.objects.filter(proyecto=proyecto, fecha_inicio__lte=date.today()).exclude(cerrado=True).order_by('fecha_inicio')
    
    checkProject(proyecto)
    
    if proyecto.estado == Proyecto.INICIADO:
        details_link = True
        
    return render(request, 'gtpros/validate_events.html', {'proyecto': proyecto, 'eventos': eventos, 'details_link': details_link, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def validate_event(request, id_proyecto, event_id):
    
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    evento = Evento.objects.get(pk=event_id)
    
    evento.cerrado = True
    if date.today().weekday() > 4:
        dias_extra = 7-date.today().weekday()
        evento.fecha_fin = date.today() + datetime.timedelta(days=dias_extra)
    else:
        evento.fecha_fin = date.today()
    evento.save()
    
#     Recalcular fechas eventos aqui
    recalcular(evento)
    if proyecto.estado == Proyecto.FINALIZADO:
        return redirect('summaries', )
    
    return redirect('validate_events', id_proyecto, )

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def preview(request, id_proyecto):
    
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    if request.session['es_jefe']:
        eventos = Evento.objects.filter(proyecto=proyecto, fecha_inicio__lte=date.today())
    else:
        eventos = Evento.objects.filter(proyecto=proyecto, fecha_inicio__lte=date.today(), rol__trabajador__user=request.user).order_by('fecha_inicio')
        
    listaInformes = defaultdict(list)
        
    for evento in eventos:
        key = evento
        informes_temp = Informe.objects.filter(rol__evento=evento, aceptado=True)
        listaInformes[key].extend(informes_temp)
    
    return render(request, 'gtpros/project_summary.html', {'proyecto': proyecto, 'informes': dict(listaInformes), })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def summaries(request):
    
    try:
        proyectos = Proyecto.objects.filter(estado=Proyecto.FINALIZADO)
    except Resumen.DoesNotExist:
        proyectos = None
            
    return render(request, 'gtpros/summaries.html', {'proyectos': proyectos})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def summary(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    listaInformes = defaultdict(list)
    
    eventos = Evento.objects.filter(proyecto=proyecto)
        
    for evento in eventos:
        key = evento
        informes_temp = Informe.objects.filter(rol__evento=evento)
        listaInformes[key].extend(informes_temp)
            
    return render(request, 'gtpros/project_summary.html', {'proyecto': proyecto, 'informes': dict(listaInformes), })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def calendar(request, id_proyecto):
    proyecto = Proyecto.objects.get(pk=id_proyecto)
    
    checkProject(proyecto)
    
    trabajador = Trabajador.objects.get(user__username=request.user.username)
    cargo = Cargo.objects.get(proyecto__id=id_proyecto, trabajador=trabajador)
    request.session['es_jefe'] = cargo.es_jefe
    
    if cargo.es_jefe:
        eventos_temp = list(Evento.objects.filter(proyecto=proyecto).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'duracion', 'rol__trabajador__user__username'))
        informes_temp = list(Informe.objects.filter(rol__evento__proyecto=proyecto).exclude(aceptado=None).values('id', 'fecha', 'aceptado', 'rol__evento__nombre', 'rol__trabajador__user__username'))
    else:
        eventos_temp = list(Evento.objects.filter(proyecto=proyecto, rol__trabajador__user=request.user).values('id', 'nombre', 'descripcion', 'cerrado', 'fecha_inicio', 'fecha_fin', 'duracion', 'rol__trabajador__user__username'))
        informes_temp = list(Informe.objects.filter(rol__evento__proyecto=proyecto, rol__trabajador__user=request.user).exclude(aceptado=None).values('id', 'fecha', 'aceptado', 'rol__evento__nombre', 'rol__trabajador__user__username'))
         
    eventos = json.dumps(eventos_temp, default=date_handler)
    informes = json.dumps(informes_temp, default=date_handler)
    
    return render(request, 'gtpros/calendar.html', {'proyecto': proyecto, 'eventos': eventos, 'informes': informes, })

# Fixes data serialization errors
def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

# Asignar fechas a los eventos
def setEventDates(proyecto):
    
    eventos = Evento.objects.filter(proyecto=proyecto)
    
    for evento in eventos:
        predecesores = Predecesor.objects.filter(evento_anterior=evento.pk)
        if predecesores.count() == 0:
            setDate(evento)
    
def setDate(evento):
    
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
    
def recalcular(evento):
    predecesores = Predecesor.objects.filter(evento_anterior=evento.pk)
    if predecesores.count() == 0:
        
        listaEventos = Evento.objects.filter(proyecto=evento.proyecto)
        finProyecto = True
    
        for item in listaEventos:
            predecesores = Predecesor.objects.filter(evento_anterior=item.pk)
            if predecesores.count() == 0:
                if not item.cerrado:
                    finProyecto = False
        
        if finProyecto:
            proyecto = evento.proyecto
            proyecto.fecha_fin = evento.fecha_fin
            proyecto.estado = Proyecto.FINALIZADO
            proyecto.save()
                
    else:
        for predecesor in predecesores:
            evento_siguiente = predecesor.evento
            
            fin = evento.fecha_fin
            if fin.weekday() == 4:
                evento_siguiente.fecha_inicio = fin + datetime.timedelta(days=3)
            else:
                evento_siguiente.fecha_inicio = fin + datetime.timedelta(days=1)
                
            calcularFechaFin(evento_siguiente)
            evento_siguiente.save()
            recalcular(evento_siguiente)
        
def calcularFechaFin(evento):
    
    if evento.duracion == 0:
        evento.fecha_fin = evento.fecha_inicio
    else:
        roles = Rol.objects.filter(evento=evento)
        num_roles = roles.count()
        
        semanas = evento.duracion / (num_roles * 40)
        horas_sueltas = evento.duracion % (num_roles * 40)
        dias_sueltos = math.ceil(horas_sueltas / 8.0)
        
        if dias_sueltos > 0:
            num_informes = semanas + 1
        else:
            num_informes = semanas
        generarInformes(evento, roles, num_informes)
        
        dias = 0
        dia = evento.fecha_inicio
        while dia.weekday() < 4 and dias_sueltos > 1:
            dia = dia + datetime.timedelta(days=1)
            dias = dias + 1
            dias_sueltos = dias_sueltos - 1
        if dias_sueltos > 1:
            dias + dias_sueltos + 2
        
        dias = dias + semanas * 7
        evento.fecha_fin = evento.fecha_inicio + datetime.timedelta(days=dias)

def generarInformes(evento, roles, num_informes):
    
    for rol in roles:
        for index in range(num_informes):
            fecha = evento.fecha_inicio + datetime.timedelta(days=index*7)
            informe = Informe(rol=rol, fecha=fecha)
            informe.save()