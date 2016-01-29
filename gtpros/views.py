# -*- coding: utf-8 -*-
from _collections import defaultdict
import logging

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect

from gtpros.forms import InformeForm, CargoForm, UploadFileForm, RolForm
from gtpros.models import Trabajador, Proyecto, Rol, Resumen, Informe, Evento, \
    Cargo, Predecesor
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def index(request):
    
    try:
        
        trabajador = Trabajador.objects.get(user__username=request.user.username)
        proyectos = Proyecto.objects.filter(cargo__trabajador=trabajador)
        
        logger.debug('Proyectos de ' + trabajador.user.username + ':')
        logger.debug(proyectos)
        
        request.session['listaProyectos'] = list(proyectos)
        
        if 'jefe' in request.session:
            del request.session['jefe']
        return render(request, 'gtpros/index.html', {})
    
    except Trabajador.DoesNotExist:
        
        logout(request)
        return redirect('index')

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def cargos(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
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
            return redirect('cargos', pk)
    else:
        form = CargoForm(proyecto=proyecto)
        
    return render(request, 'gtpros/workers.html', {'proyecto': proyecto, 'form': form, 'jefe': jefe, 'trabajadores': trabajadores})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def delete_worker(request, pk, worker):
    
    Cargo.objects.get(proyecto=pk, trabajador__pk=worker).delete()
    
    return redirect('cargos', pk)

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def importar(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    if request.POST:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            procesar_archivo(proyecto, request.FILES['file'])
            
            proyecto.estado = Proyecto.ASIGNACION
            proyecto.save()
            
            return redirect('roles', pk)
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
        modelActividad = Evento(id_evento=actividad_id, proyecto=proyecto, nombre=nom, descripcion=desc, duracion=dur)
        modelActividad.save()
        for predecesor in actividad["predecesores"]:
            evento_previo = Evento.objects.get(id_evento=predecesor["id"], proyecto=proyecto)
            modelPredecesor = Predecesor(evento=modelActividad, evento_anterior=evento_previo)
            listaPredecesores.append(modelPredecesor)
        for rol in actividad["roles"]:
            tipo = rol["tipo"]
            cant = rol["cantidad"]
            for i in range(cant):
                modelRol = Rol(evento=modelActividad, tipo_rol=tipo)
                modelRol.save()
    
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
def roles(request, pk, role=None):
    proyecto = Proyecto.objects.get(pk=pk)
    
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
                    return redirect('roles', pk)
                else:
                    return redirect('roles_add', pk, rol)
            else:
                logger.debug("DELETE")
                rol_to_edit.delete()
                return redirect('roles', pk)
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

    return render(request, 'gtpros/roles.html', {'proyecto': proyecto, 'form': form, 'roles': dict(roles)})

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
def actividades(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    eventos = Evento.objects.filter(proyecto=proyecto, rol__trabajador__user=request.user)
    
    return render(request, 'gtpros/activities.html', {'proyecto': proyecto, 'eventos': eventos, })


@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def events(request, pk, type):
    proyecto = Proyecto.objects.get(pk=pk)
    
    eventos = Evento.objects.filter(proyecto=proyecto)
    
    return render(request, 'gtpros/activities.html', {'proyecto': proyecto, 'eventos': eventos, })

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def new_report(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    user = request.user
    actividades = Evento.objects.filter(rol__trabajador__user=user)
    
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
    
    if request.session['jefe']:
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
def validate_event(request, pk):
    
    id = request.POST['actividad']
    evento = Evento.objects.get(pk=id)
    
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
            
    return render(request, 'gtpros/project_summary.html', {'proyecto': proyecto, 'resumen': resumen})

def actividad_detalle(request):
    id = request.GET.get('id', '')
    evento = Evento.objects.get(pk=id)
    
    return render(request, 'gtpros/event_detail.html', {'evento': evento, 'tipo': 'A'})

def hito_detalle(request):
    id = request.GET.get('id', '')
    evento = Evento.objects.get(pk=id)
    
    return render(request, 'gtpros/event_detail.html', {'evento': evento, 'tipo': 'H'})

@login_required
@user_passes_test(lambda u: not u.is_superuser)    
def calendar(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    
    trabajador = Trabajador.objects.get(user__username=request.user.username)
    cargo = Cargo.objects.get(proyecto__id=pk, trabajador=trabajador)
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