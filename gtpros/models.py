# -*- encoding: utf-8 -*-
from django.db import models

class Trabajador(models.Model):
    DNI = models.CharField(max_length=9, primary_key=True)
    nombre = models.CharField(max_length=20)
    apellidos = models.CharField(max_length=20)
    
class Categoria(models.Model):
    trabajador = models.ForeignKey('Trabajador')
    proyecto = models.ForeignKey('Proyecto')
    
    JEFE = 'JF'
    ANALISTA = 'AN'
    DISEÑADOR = 'DI'
    ANALISTA_PROG = 'AP'
    RESPONSABLE = 'RE'
    PROGRAMADOR = 'PR'
    PROBADOR = 'QA'
    
    TIPO_OPCIONES = (
        (JEFE, 'Jefe'),
        (ANALISTA, 'Analista'),
        (DISEÑADOR, 'Diseñador'),
        (ANALISTA_PROG, 'Analista Programador'),
        (RESPONSABLE, 'Responsable'),
        (PROGRAMADOR, 'Programador'),
        (PROBADOR, 'Probador'),
    )
    tipo = models.CharField(max_length=2, choices=TIPO_OPCIONES)
    
    class Meta:
        unique_together = (("trabajador", "proyecto"),)
    
class Proyecto(models.Model):
    nombre = models.CharField(max_length=20)
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)
    
class Resumen(models.Model):
    proyecto = models.ForeignKey('Proyecto')
    descripcion = models.TextField()

class Informe(models.Model):
    descripcion = models.CharField(max_length=20)
    actividad = models.ForeignKey('Actividad')
    
class Actividad(models.Model):
    duracion = models.IntegerField()
    proyecto = models.ForeignKey('Proyecto')
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()