# -*- encoding: utf-8 -*-
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _

class Trabajador(models.Model):
    user = models.OneToOneField('auth.User', primary_key=True)
    dni = models.CharField(max_length=9,
       help_text=_('Required. 9 characters. Format: 71254631D.'),
       validators=[
           validators.RegexValidator(r'^\d{8}[A-Z]{1}$', _('Introduce un DNI valido. Formato: 71254631D.')
             ),
       ],
    verbose_name='DNI', blank=True, null=True)
    
    categoria = models.IntegerField()
    
    def __str__(self):
        if self.user.last_name and self.user.first_name:
            output = ''.join([self.user.last_name, ', ', self.user.first_name])
        else:
            output = self.user.username
        return ''.join([output, ' - ', str(self.categoria)])
        
    class Meta:
        verbose_name_plural = "Trabajadores"
    
class Cargo(models.Model):
    proyecto = models.ForeignKey('Proyecto')
    trabajador = models.ForeignKey('Trabajador')
    es_jefe = models.BooleanField(default=True, verbose_name="¿Jefe del Proyecto?")
    
    def validate_unique(self, exclude=None):
        qs = self.__class__.objects.filter(trabajador=self.trabajador)
        if qs.filter(proyecto=self.proyecto).exists():
            raise ValidationError('El trabajador ya tiene un cargo asignado en este proyecto.')
        
    def validate_boss_duplicate(self):
        if self.es_jefe != True:
            return
        existing = self.__class__.objects.filter(proyecto=self.proyecto).count()
        if existing > 0:
            raise ValidationError(
                "Un mismo proyecto no puede tener más de un Jefe de Proyecto."
            )
            
    class Meta:
        unique_together = (("trabajador", "proyecto"),)
        
    def __str__(self):
        return ''.join([str(self.proyecto), ': ', str(self.trabajador)])
    
class Rol(models.Model):
    trabajador = models.ForeignKey('Trabajador')
    evento = models.ForeignKey('Evento')
    
    tipo_rol = models.ForeignKey('TipoRol', verbose_name="Tipo de Rol")
            
    class Meta:
        verbose_name_plural = "Roles"
        unique_together = (("trabajador", "evento"),)
        
    def __str__(self):
        return ''.join([str(self.trabajador), ' - ', self.tipo_rol.nombre])

class TipoRol(models.Model):
    nombre = models.CharField(max_length=30, null=False)
    siglas = models.CharField(max_length=2, null=False, unique=True)
    min_cat = models.IntegerField(verbose_name="Categoría mínima")
    
    class Meta:
        verbose_name_plural = "Tipos de Rol"
        verbose_name = "Tipo de Rol"
        
    def __str__(self):
        return ''.join([self.nombre, ' - ', str(self.min_cat)])

class Proyecto(models.Model):
    nombre = models.CharField(max_length=30, null=False,
        help_text=_('Obligatorio. Maximo 30 caracteres.'),
    )
    descripcion = models.TextField(max_length=200,
        help_text=_('Un maximo de 200 caracteres.'), blank=True)
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name="Fecha inicial")
    fecha_fin = models.DateField(blank=True, null=True, verbose_name="Fecha final")
    
    NUEVO = 'N'
    CALENDARIZACION = 'C'
    ASIGNACION = 'A'
    PREPARADO = 'P'
    INICIADO = 'I'
    FINALIZADO = 'F'
    
    ESTADO_OPCIONES = (
        (NUEVO, 'Inicial'),
        (CALENDARIZACION, 'Calendarización'),
        (ASIGNACION, 'Asignación'),
        (PREPARADO, 'Preparado'),
        (INICIADO, 'Iniciado'),
        (FINALIZADO, 'Finalizado')
    )
    
    estado = models.CharField(max_length=1, choices=ESTADO_OPCIONES, default=NUEVO)
    
    def validate_date_coherence(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError(
                "La fecha de finalización debe ser posterior a la de inicio."
            )
    
    def __str__(self):
        return ''.join([self.nombre, ' (', self.get_estado_display(), ')'])
    
class Resumen(models.Model):
    proyecto = models.OneToOneField('Proyecto', primary_key=True)
    descripcion = models.TextField()
    
    class Meta:
        verbose_name_plural = "Resumenes"

class Informe(models.Model):
    descripcion = models.TextField(blank=True, null=True)
    evento = models.ForeignKey('Evento')
    rol = models.ForeignKey('Rol')
    aceptado = models.NullBooleanField(blank=True, null=True)
    fecha = models.DateField(default=timezone.now)
    
    lunes = models.IntegerField(blank=True, null=True)
    martes = models.IntegerField(blank=True, null=True)
    miercoles = models.IntegerField(blank=True, null=True)
    jueves = models.IntegerField(blank=True, null=True)
    viernes = models.IntegerField(blank=True, null=True)
    
    def aceptar(self):
        self.aceptado = True
    
    def rechazar(self):
        self.aceptado = False
    
class Evento(models.Model):
    id_evento = models.IntegerField()
    proyecto = models.ForeignKey('Proyecto')
    nombre = models.CharField(max_length = 20)
    descripcion = models.TextField(max_length = 200)
    cerrado = models.BooleanField(default = False)
    fecha_inicio = models.DateField(null=True, verbose_name="Fecha inicial")
    fecha_fin = models.DateField(null=True, verbose_name="Fecha final")
    duracion = models.IntegerField(default = 0, verbose_name="Duración en horas/hombre")
    tipo_rol = models.ForeignKey('TipoRol', blank=True, null=True, verbose_name="Tipo de rol requerido")
    
    def validate_date_coherence(self):
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError(
                "La fecha de finalización debe ser posterior a la de inicio."
            )
            
    def save(self, *args, **kwargs):
 
        self.validate_date_coherence()
 
        super(Evento, self).save(*args, **kwargs)
        
    class Meta:
        unique_together = (("id_evento", "proyecto"),)
        
    def __str__(self):
        if self.duracion == 0:
            return ''.join(['[HITO] ', self.nombre])
        else:
            return ''.join(['[ACTIVIDAD] ', self.nombre, ' (', str(self.duracion), ' horas/hombre)'])
        
class Predecesor(models.Model):
    evento = models.ForeignKey('Evento', related_name='evento')
    evento_anterior = models.ForeignKey('Evento', related_name='evento_anterior')
    