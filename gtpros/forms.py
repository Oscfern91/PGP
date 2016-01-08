from django import forms
from gtpros.models import Rol, Resumen, Informe

class RolForm(forms.ModelForm):
    tipo_rol = forms.ChoiceField(label='Rol')

    def __init__(self, *args, **kwargs):
        super(RolForm, self).__init__(*args, **kwargs)

        excluded = Rol.JEFE_PROYECTO
        self.fields['tipo_rol'].choices = [(k, v) for k, v in Rol.ROL_OPCIONES if k not in excluded]

    class Meta:
        model = Rol
        fields = ('trabajador', 'tipo_rol',)

class ResumenForm(forms.ModelForm):
    descripcion=forms.CharField(label='Resumen', widget=forms.Textarea)

    class Meta:
        model = Resumen
        fields = ('descripcion', )
    
class InformeForm(forms.ModelForm):
    descripcion=forms.CharField(label='Informe', widget=forms.Textarea)
    
    class Meta:
        model = Informe
        fields = ('descripcion', )