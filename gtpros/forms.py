from django import forms
from django.contrib.admin import widgets

from gtpros.models import Rol, Resumen, Informe, Actividad, Hito

import floppyforms
import logging
from django.core.exceptions import ValidationError

# Get an instance of a logger
logger = logging.getLogger(__name__)

class RolForm(forms.ModelForm):
    tipo_rol = forms.ChoiceField(label='Rol')
    readonly_fields = ('proyecto',)

    def __init__(self, *args, **kwargs):
        super(RolForm, self).__init__(*args, **kwargs)

        excluded = Rol.JEFE_PROYECTO
        self.fields['tipo_rol'].choices = [(k, v) for k, v in Rol.ROL_OPCIONES if k not in excluded]
        
        self.fields['proyecto'].widget = forms.HiddenInput()

    class Meta:
        model = Rol
        fields = ('trabajador', 'tipo_rol', 'proyecto',)

class ResumenForm(forms.ModelForm):
    descripcion = forms.CharField(label='Resumen', widget=forms.Textarea)

    class Meta:
        model = Resumen
        fields = ('descripcion',)
    
class InformeForm(forms.ModelForm):
    descripcion = forms.CharField(label='Informe', widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(InformeForm, self).__init__(*args, **kwargs)
        
        self.fields['actividad'].widget = forms.HiddenInput()
    
    class Meta:
        model = Informe
        fields = ('descripcion', 'actividad', )
        
class ActividadForm(forms.ModelForm):
    fecha_inicio = floppyforms.SplitDateTimeField()
    fecha_fin = floppyforms.SplitDateTimeField()
    
    
    def __init__(self, *args, **kwargs):
        if 'proyecto' in kwargs:
            proyecto = kwargs.pop('proyecto')
        else:
            proyecto = None
        
        super(ActividadForm, self).__init__(*args, **kwargs)
        
        if proyecto:
            self.fields['rol'].queryset = Rol.objects.filter(proyecto=proyecto).exclude(tipo_rol=Rol.JEFE_PROYECTO)
            self.fields['proyecto'].widget = forms.HiddenInput()
            self.fields['proyecto'].initial = proyecto
            
        self.fields['type'] = forms.CharField(widget = forms.HiddenInput())
        self.fields['type'].initial = 'A' 
        self.fields['rol'].label = ''
        
    def clean(self):
        super(ActividadForm, self).clean()
        
        data = self.cleaned_data
        if data['fecha_fin'] < data['fecha_inicio']:
            raise ValidationError(
                "La fecha de finalizacion debe ser posterior a la de inicio."
            )
        return data
    
    class Meta:
        model = Actividad
        fields = ('nombre', 'descripcion', 'rol', 'fecha_inicio', 'fecha_fin', 'proyecto', )
        
class HitoForm(forms.ModelForm):
    fecha = floppyforms.SplitDateTimeField()

    def __init__(self, *args, **kwargs):
        super(HitoForm, self).__init__(*args, **kwargs)
        
        self.fields['proyecto'].widget = forms.HiddenInput()
        
        self.fields['type'] = forms.CharField(widget = forms.HiddenInput())
        self.fields['type'].initial = 'H' 
        
    class Meta:
        model = Hito
        fields = ('nombre', 'descripcion', 'fecha', 'proyecto', )
        