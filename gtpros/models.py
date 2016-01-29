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
    es_jefe = models.BooleanField(default=True)
    
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
    
class Rol(models.Model):
    trabajador = models.ForeignKey('Trabajador', blank=True, null=True)
    evento = models.ForeignKey('Evento')
    
    ANALISTA = 'AN'
    DISENADOR = 'DI'
    ANALISTA_PROG = 'AP'
    RESPONSABLE_PRUEBAS = 'RP'
    PROGRAMADOR = 'PG'
    PROBADOR = 'QA'
    
    ROL_OPCIONES = (
        (ANALISTA, 'Analista'),
        (DISENADOR, 'Diseñador'),
        (ANALISTA_PROG, 'Analista Programador'),
        (RESPONSABLE_PRUEBAS, 'Responsable'),
        (PROGRAMADOR, 'Programador'),
        (PROBADOR, 'Probador'),
    )
    
    tipo_rol = models.CharField(max_length=2, choices=ROL_OPCIONES)
            
    class Meta:
        verbose_name_plural = "Roles"
        
    def __str__(self):
        return ''.join([str(self.trabajador), ' - ', self.get_tipo_rol_display()])
    
class Proyecto(models.Model):
    nombre = models.CharField(max_length=20, null=False,
        help_text=_('Obligatorio. Maximo 20 caracteres.'),
    )
    descripcion = models.TextField(max_length=200,
        help_text=_('Un maximo de 200 caracteres.'), blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    
    NUEVO = 'N'
    ASIGNACION = 'A'
    PREPARADO = 'P'
    INICIADO = 'I'
    FINALIZADO = 'F'
    
    ESTADO_OPCIONES = (
        (NUEVO, 'Inicial'),
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
        return self.nombre
    
class Resumen(models.Model):
    proyecto = models.OneToOneField('Proyecto', primary_key=True)
    descripcion = models.TextField()
    
    class Meta:
        verbose_name_plural = "Resumenes"

class Informe(models.Model):
    descripcion = models.TextField()
    evento = models.ForeignKey('Evento')
    aceptado = models.NullBooleanField(blank=True, null=True)
    fecha = models.DateTimeField(default=timezone.now)
    
    lunes = models.IntegerField()
    martes = models.IntegerField()
    miercoles = models.IntegerField()
    jueves = models.IntegerField()
    viernes = models.IntegerField()
    
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
    fecha_inicio = models.DateTimeField(null=True)
    fecha_fin = models.DateTimeField(null=True)
    duracion = models.IntegerField(default = 0)
    
    def validate_date_coherence(self):
        if self.fecha_inicio > self.fecha_fin:
            raise ValidationError(
                "La fecha de finalización debe ser posterior a la de inicio."
            )
            
    def save(self, *args, **kwargs):
 
        self.validate_date_coherence()
 
        super(Evento, self).save(*args, **kwargs)
        
    class Meta:
        unique_together = (("id", "proyecto"),)
        
class Predecesor(models.Model):
    evento = models.ForeignKey('Evento', related_name='evento')
    evento_anterior = models.ForeignKey('Evento', related_name='evento_anterior', blank=True, null=True)
    