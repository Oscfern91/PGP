# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-27 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gtpros', '0003_auto_20160127_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cargo',
            name='es_jefe',
            field=models.BooleanField(default=True),
        ),
    ]
