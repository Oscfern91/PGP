from django import forms

from gtpros.models import Rol, Resumen, Informe, Evento, Cargo, Trabajador,\
    Proyecto

import floppyforms
import logging
from django.core.exceptions import ValidationError

# Get an instance of a logger
logger = logging.getLogger(__name__)

class CargoForm(forms.ModelForm):

    readonly_fields = ('proyecto',)
    
    def __init__(self, *args, **kwargs):
        proyecto = kwargs.pop('proyecto', None)
        super(CargoForm, self).__init__(*args, **kwargs)
        
        if proyecto:
            self.fields['proyecto'].initial = proyecto
            self.fields['trabajador'].queryset = Trabajador.objects.all().exclude(cargo__proyecto = proyecto)
        
        self.fields['proyecto'].widget = forms.HiddenInput()
        self.fields['es_jefe'].widget = forms.HiddenInput()
        self.fields['es_jefe'].initial = False
        
    class Meta:
        model = Cargo
        fields = ('trabajador', 'proyecto', 'es_jefe')
        
class InformeForm(forms.ModelForm):
    descripcion = forms.CharField(label='Informe', widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(InformeForm, self).__init__(*args, **kwargs)
        
        self.fields['evento'].widget = forms.HiddenInput()
    
    class Meta:
        model = Informe
        fields = ('descripcion', 'evento', )

class UploadFileForm(forms.Form):
    file = forms.FileField(label='Archivo JSON')

class RolForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        if 'evento' in kwargs:
            evento = kwargs.pop('evento')
        else:
            evento = None
        super(RolForm, self).__init__(*args, **kwargs)
        
        if evento:
            self.fields['evento'].initial = evento
            self.fields['tipo_rol'].initial = evento.tipo_rol
            
        self.fields['evento'].widget = forms.HiddenInput()
        self.fields['tipo_rol'].widget = forms.HiddenInput()
        
    class Meta:
        model = Rol
        fields = '__all__'

class ProjectForm(forms.ModelForm):
    fecha_inicio = floppyforms.DateField()
    fecha_fin = floppyforms.DateField()
    
    def clean(self):
        super(ProjectForm, self).clean()
        
        data = self.cleaned_data
        if data['fecha_fin'] < data['fecha_inicio']:
            raise ValidationError(
                "La fecha de finalizacion debe ser posterior a la de inicio."
            )
        return data
    
    class Meta:
        model = Proyecto
        fields = ('fecha_inicio', 'fecha_fin')
