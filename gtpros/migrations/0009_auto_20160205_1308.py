# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-05 12:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gtpros', '0008_auto_20160203_1742'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='evento',
            unique_together=set([('id_evento', 'proyecto')]),
        ),
    ]