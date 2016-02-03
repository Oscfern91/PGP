import logging

from django.contrib import admin

from gtpros.models import Trabajador, Proyecto, Cargo
from django.forms.models import BaseInlineFormSet


# Get an instance of a logger
logger = logging.getLogger(__name__)

class CargoInline(admin.TabularInline):
    model = Cargo
    max_num = 1
    readonly_fields = ('es_jefe',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "trabajador":
            kwargs["queryset"] = Trabajador.objects.filter(categoria=1).exclude(cargo__es_jefe=True)
        return super(CargoInline, self).formfield_for_foreignkey(db_field, request, **kwargs)
    
class ProyectoAdmin(admin.ModelAdmin):
    model = Proyecto
    inlines = (CargoInline,)
    
    def get_form(self, request, obj=None, **kwargs):
        self.exclude = ("estado", "fecha_inicio", "fecha_fin")
        form = super(ProyectoAdmin, self).get_form(request, obj, **kwargs)
        return form

admin.site.register(Trabajador)
admin.site.register(Proyecto, ProyectoAdmin)