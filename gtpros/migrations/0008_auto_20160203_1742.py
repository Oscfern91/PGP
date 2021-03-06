# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-03 16:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gtpros', '0007_auto_20160203_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='fecha_fin',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='fecha_inicio',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='informe',
            name='fecha',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='proyecto',
            name='fecha_inicio',
            field=models.DateField(blank=True, null=True),
        ),
    ]
