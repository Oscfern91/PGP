# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-28 12:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtpros', '0005_auto_20160128_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='fecha_fin',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='evento',
            name='fecha_inicio',
            field=models.DateTimeField(null=True),
        ),
    ]