from django.contrib import admin
from gtpros.models import Trabajador, Proyecto, Rol
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class RolInline(admin.TabularInline):
    model = Rol
    max_num = 1
    readonly_fields = ('tipo_rol',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "trabajador":
            kwargs["queryset"] = Trabajador.objects.filter(categoria=Trabajador.JEFE)
        return super(RolInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class ProyectoAdmin(admin.ModelAdmin):
    model = Proyecto
    inlines = (RolInline,)

admin.site.register(Trabajador)
admin.site.register(Proyecto, ProyectoAdmin)