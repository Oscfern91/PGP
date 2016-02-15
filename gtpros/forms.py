from django import forms

from gtpros.models import Rol, Informe, Cargo, Trabajador, \
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
            exclusiones = Trabajador.objects.exclude(cargo__proyecto__estado=Proyecto.FINALIZADO).filter(cargo__es_jefe=True).filter(cargo__es_jefe=False)
            self.fields['trabajador'].queryset = Trabajador.objects.all().exclude(cargo__proyecto=proyecto).exclude(pk__in=exclusiones)
        
        self.fields['proyecto'].widget = forms.HiddenInput()
        self.fields['es_jefe'].widget = forms.HiddenInput()
        self.fields['es_jefe'].initial = False
        
    class Meta:
        model = Cargo
        fields = ('trabajador', 'proyecto', 'es_jefe')
        
class InformeForm(forms.ModelForm):
    
    suma_total = forms.IntegerField()
    descripcion = forms.CharField(label='Notas del informe', widget=forms.Textarea(attrs={'placeholder': 'Por ejemplo: La actividad esta lista para finalizar.'}))
    
    def __init__(self, *args, **kwargs):
        super(InformeForm, self).__init__(*args, **kwargs)
        self.fields['rol'].widget = forms.HiddenInput()
        self.fields['suma_total'].widget.attrs['readonly'] = True
        
        for key in self.fields:
            self.fields[key].required = False
        
    def clean(self, commit=True):
        form_data = self.cleaned_data
        suma_total = form_data.get('suma_total', None)
        if suma_total > 40:
            raise ValidationError(
                "La suma de horas no puede ser mayor a 40."
            )
        return form_data
    
    class Meta:
        model = Informe
        fields = ('tarea1', 'tarea2', 'tarea3', 'tarea4', 'tarea5', 'tarea6', 'descripcion', 'rol')

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
            jefe = Trabajador.objects.filter(cargo__proyecto=evento.proyecto, cargo__es_jefe=True)
            self.fields['trabajador'].queryset = Trabajador.objects.filter(cargo__proyecto=evento.proyecto, categoria__lte=evento.tipo_rol.min_cat).exclude(pk=jefe)
            
        self.fields['evento'].widget = forms.HiddenInput()
        self.fields['tipo_rol'].widget = forms.HiddenInput()
        
    class Meta:
        model = Rol
        fields = '__all__'

class ProjectForm(forms.ModelForm):
    fecha_inicio = floppyforms.DateField()
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['fecha_fin'].widget = forms.HiddenInput()
        
    class Meta:
        model = Proyecto
        fields = ('fecha_inicio', 'fecha_fin')
