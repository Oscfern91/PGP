# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-09 21:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtpros', '0015_informe_enviado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proyecto',
            name='estado',
            field=models.CharField(choices=[(b'N', b'Inicial'), (b'C', b'Calendarizacion'), (b'A', b'Asignacion'), (b'P', b'Preparado'), (b'I', b'Iniciado'), (b'F', b'Finalizado')], default=b'N', max_length=1),
        ),
        migrations.AlterField(
            model_name='tiporol',
            name='min_cat',
            field=models.IntegerField(verbose_name=b'Categoria minima'),
        ),
    ]
