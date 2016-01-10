# -*- encoding: utf-8 -*-
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext as _
from pip.cmdoptions import editable


class Trabajador(models.Model):
    user = models.OneToOneField('auth.User', primary_key=True)
    dni = models.CharField(max_length=9,
       help_text=_('Required. 9 characters. Format: 71254631D.'),
       validators=[
           validators.RegexValidator(r'^\d{8}[A-Z]{1}$', _('Introduce un DNI valido. Formato: 71254631D.')
             ),
       ],
    verbose_name='DNI', blank=True, null=True)
    
    JEFE = 'J'
    DESARROLLADOR = 'D'
    
    CATEGORIA_OPCIONES = (
        (JEFE, 'Jefe'),
        (DESARROLLADOR, 'Desarrollador'),
    )
    
    categoria = models.CharField(max_length=1, choices=CATEGORIA_OPCIONES)
    
    def __str__(self):
        if self.user.last_name and self.user.first_name:
            return ''.join([self.user.last_name, ', ', self.user.first_name])
        else:
            return self.user.username
        
    class Meta:
        verbose_name_plural = "Trabajadores"
    
class Rol(models.Model):
    trabajador = models.ForeignKey('Trabajador')
    proyecto = models.ForeignKey('Proyecto')
    
    JEFE_PROYECTO = 'JP'
    ANALISTA = 'AN'
    DISEÑADOR = 'DI'
    ANALISTA_PROG = 'AP'
    RESPONSABLE = 'RE'
    PROGRAMADOR = 'PR'
    PROBADOR = 'QA'
    
    ROL_OPCIONES = (
        (JEFE_PROYECTO, 'Jefe de Proyecto'),
        (ANALISTA, 'Analista'),
        (DISEÑADOR, 'Diseñador'),
        (ANALISTA_PROG, 'Analista Programador'),
        (RESPONSABLE, 'Responsable'),
        (PROGRAMADOR, 'Programador'),
        (PROBADOR, 'Probador'),
    )
    
    tipo_rol = models.CharField(max_length=2, choices=ROL_OPCIONES, default=JEFE_PROYECTO)
    
    def validate_unique(self, exclude=None):
        qs = self.__class__.objects.filter(trabajador=self.trabajador)
        if qs.filter(proyecto=self.proyecto).exists():
            raise ValidationError('El trabajador ya tiene un rol asignado en este proyecto.')
    
    def validate_boss_duplicate(self):
        if self.tipo_rol != self.JEFE_PROYECTO:
            return
        existing = self.__class__.objects.filter(proyecto=self.proyecto).count()
        if existing > 0:
            raise ValidationError(
                "Un mismo proyecto no puede tener más de un Jefe de Proyecto."
            )
            
    def save(self, *args, **kwargs):
 
        self.validate_unique()
        self.validate_boss_duplicate()
 
        super(Rol, self).save(*args, **kwargs)
    
    class Meta:
        unique_together = (("trabajador", "proyecto"),)
        verbose_name_plural = "Roles"
        
    def __str__(self):
        return ''.join([str(self.trabajador), ' - ', self.get_tipo_rol_display()])
    
class Proyecto(models.Model):
    nombre = models.CharField(max_length=20, null=False,
        help_text=_('Obligatorio. Maximo 20 caracteres.'),
    )
    descripcion = models.TextField(max_length=200,
        help_text=_('Un maximo de 200 caracteres.'), blank=True)
    activo = models.BooleanField(default=True,
        help_text=_('Indica si el proyecto se encuentra abierto o cerrado.'),
    )
    
    def __str__(self):
        return self.nombre
    
class Resumen(models.Model):
    proyecto = models.OneToOneField('Proyecto', primary_key=True)
    descripcion = models.TextField()
    
    class Meta:
        verbose_name_plural = "Resumenes"

class Informe(models.Model):
    descripcion = models.TextField()
    actividad = models.ForeignKey('Actividad')
    aceptado = models.NullBooleanField(blank=True, null=True)
    fecha = models.DateTimeField(default = timezone.now)
    
    def aceptar(self):
        self.aceptado = True
    
    def rechazar(self):
        self.aceptado = False
    
class Evento(models.Model):
    proyecto = models.ForeignKey('Proyecto')
    nombre = models.CharField(max_length=20)
    descripcion = models.TextField(max_length=200)
    
class Hito(Evento):
    fecha = models.DateTimeField()
    
class Actividad(Evento):
    rol = models.ForeignKey('Rol')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    
    def validate_date_coherence(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError(
                "La fecha de finalización debe ser posterior a la de inicio."
            )
            
    def save(self, *args, **kwargs):
 
        self.validate_date_coherence()
 
        super(Actividad, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Actividades"
