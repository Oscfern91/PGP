from django.contrib import admin
from gtpros.models import Trabajador, Proyecto, Categoria

class CategoriaInline(admin.TabularInline):
    model = Categoria
    list_filter = ('trabajador__nombre')

class ProyectoAdmin(admin.ModelAdmin):
    model = Proyecto
    inlines = (CategoriaInline,)

admin.site.register(Trabajador)
admin.site.register(Proyecto, ProyectoAdmin)
