# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-05 12:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gtpros', '0009_auto_20160205_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='predecesor',
            name='evento_anterior',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='evento_anterior', to='gtpros.Evento'),
            preserve_default=False,
        ),
    ]
