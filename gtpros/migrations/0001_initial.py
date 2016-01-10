# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-10 00:05
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Informe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField()),
                ('aceptado', models.NullBooleanField()),
                ('fecha', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Proyecto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(help_text='Obligatorio. Maximo 20 caracteres.', max_length=20)),
                ('descripcion', models.TextField(blank=True, help_text='Un maximo de 200 caracteres.', max_length=200)),
                ('activo', models.BooleanField(default=True, help_text='Indica si el proyecto se encuentra abierto o cerrado.')),
            ],
        ),
        migrations.CreateModel(
            name='Rol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_rol', models.CharField(choices=[('JP', 'Jefe de Proyecto'), ('AN', 'Analista'), ('DI', 'Diseñador'), ('AP', 'Analista Programador'), ('RE', 'Responsable'), ('PR', 'Programador'), ('QA', 'Probador')], default='JP', max_length=2)),
            ],
            options={
                'verbose_name_plural': 'Roles',
            },
        ),
        migrations.CreateModel(
            name='Trabajador',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('dni', models.CharField(blank=True, help_text='Required. 9 characters. Format: 71254631D.', max_length=9, null=True, validators=[django.core.validators.RegexValidator('^\\d{8}[A-Z]{1}$', 'Introduce un DNI valido. Formato: 71254631D.')], verbose_name='DNI')),
                ('categoria', models.CharField(choices=[('J', 'Jefe'), ('D', 'Desarrollador')], max_length=1)),
            ],
            options={
                'verbose_name_plural': 'Trabajadores',
            },
        ),
        migrations.CreateModel(
            name='Actividad',
            fields=[
                ('evento_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gtpros.Evento')),
                ('fecha_inicio', models.DateTimeField()),
                ('fecha_fin', models.DateTimeField()),
            ],
            options={
                'verbose_name_plural': 'Actividades',
            },
            bases=('gtpros.evento',),
        ),
        migrations.CreateModel(
            name='Hito',
            fields=[
                ('evento_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='gtpros.Evento')),
                ('fecha', models.DateTimeField()),
            ],
            bases=('gtpros.evento',),
        ),
        migrations.CreateModel(
            name='Resumen',
            fields=[
                ('proyecto', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='gtpros.Proyecto')),
                ('descripcion', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Resumenes',
            },
        ),
        migrations.AddField(
            model_name='rol',
            name='proyecto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtpros.Proyecto'),
        ),
        migrations.AddField(
            model_name='rol',
            name='trabajador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtpros.Trabajador'),
        ),
        migrations.AddField(
            model_name='evento',
            name='proyecto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtpros.Proyecto'),
        ),
        migrations.AlterUniqueTogether(
            name='rol',
            unique_together=set([('trabajador', 'proyecto')]),
        ),
        migrations.AddField(
            model_name='informe',
            name='actividad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtpros.Actividad'),
        ),
        migrations.AddField(
            model_name='actividad',
            name='rol',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gtpros.Rol'),
        ),
    ]
