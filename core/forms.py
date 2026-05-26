from django import forms
from .models import StaffProfile, Area, Proceso, Paso, EjecucionProceso, EjecucionPaso, Planificacion
from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget

class StaffForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Nombre de usuario')
    first_name = forms.CharField(max_length=30, label='Nombre(s)')
    last_name = forms.CharField(max_length=150, label='Apellidos')
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text='Dejar en blanco para no cambiar')
    equipo_a_cargo = forms.ModelMultipleChoiceField(queryset=StaffProfile.objects.none(), required=False, label='Equipo a cargo')
    
    class Meta:
        model = StaffProfile
        fields = ['rol', 'area_asignada', 'minimo_porcentaje', 'procesos_asignados',
                  'puede_gestionar_staff', 'puede_gestionar_areas', 'puede_gestionar_procesos', 'puede_gestionar_pasos', 'puede_supervisar',
                  'equipo_a_cargo']
        widgets = {
            'procesos_asignados': forms.SelectMultiple(attrs={'size': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['equipo_a_cargo'].queryset = StaffProfile.objects.exclude(pk=self.instance.pk)
            self.fields['equipo_a_cargo'].initial = self.instance.equipo_a_cargo.all()
        else:
            self.fields['equipo_a_cargo'].queryset = StaffProfile.objects.none()
    
    def save(self, commit=True):
        staff = super().save(commit=False)
        if commit:
            staff.save()
            self.save_m2m()
            # Actualizar relación many-to-many de equipo a cargo
            if self.cleaned_data.get('equipo_a_cargo'):
                staff.equipo_a_cargo.set(self.cleaned_data['equipo_a_cargo'])
            else:
                staff.equipo_a_cargo.clear()
        return staff

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre', 'descripcion', 'responsable', 'minimo_requerido']

class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Proceso
        fields = ['nombre', 'area', 'objetivo', 'video_ayuda', 'nivel_critico', 'tiempo_estimado', 'activo']

class PasoForm(forms.ModelForm):
    ayuda_html = forms.CharField(widget=CKEditorWidget(), required=False, label='Ayuda (HTML)')
    
    class Meta:
        model = Paso
        fields = ['nombre', 'descripcion', 'tipo', 'puntos', 'orden', 'ayuda_html', 
                  'pregunta_condicion', 'paso_si', 'paso_no', 'nivel_critico', 'evidencia_tipo']
    
    def __init__(self, *args, **kwargs):
        proceso_id = kwargs.pop('proceso_id', None)
        super().__init__(*args, **kwargs)
        if proceso_id:
            pasos_qs = Paso.objects.filter(proceso_id=proceso_id)
            self.fields['paso_si'].queryset = pasos_qs
            self.fields['paso_no'].queryset = pasos_qs

class PlanificacionForm(forms.ModelForm):
    class Meta:
        model = Planificacion
        fields = ['proceso', 'frecuencia', 'regla', 'fecha_inicio', 'fecha_fin', 'activo', 'usuario_asignado']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SupervisionPasoForm(forms.ModelForm):
    class Meta:
        model = EjecucionPaso
        fields = ['puntaje_ajustado', 'comentario_supervision']

class SupervisionGeneralForm(forms.ModelForm):
    class Meta:
        model = EjecucionProceso
        fields = ['comentario_general', 'resultado_supervision']
