from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.db.models.signals import post_save
from django.dispatch import receiver

# Roles predefinidos
ROLES = (
    ('admin', 'Administrador'),
    ('supervisor', 'Supervisor'),
    ('auditor', 'Auditor'),
    ('operador', 'Operador'),
)

CRITICIDAD = (
    ('baja', 'Baja'),
    ('media', 'Media'),
    ('alta', 'Alta'),
)

ESTADO_EJECUCION = (
    ('en_progreso', 'En progreso'),
    ('completado', 'Completado'),
    ('cancelado', 'Cancelado'),
    ('supervisado', 'Supervisado'),
    ('auditado', 'Auditado'),
)

TIPO_PASO = (
    ('normal', 'Normal'),
    ('condicional', 'Condicional'),
)

TIPO_EVIDENCIA = (
    ('ninguna', 'Ninguna'),
    ('fotografica', 'Solo fotográfica'),
    ('descriptiva', 'Solo descriptiva'),
    ('ambas', 'Fotográfica y descriptiva'),
)

FRECUENCIA_RECURRENCIA = (
    ('diaria', 'Diaria'),
    ('semanal', 'Semanal'),
    ('mensual', 'Mensual'),
)

ESTADO_SUPERVISION = (
    ('pendiente', 'Pendiente'),
    ('en_revision', 'En revisión'),
    ('aprobado', 'Aprobado'),
    ('rechazado', 'Rechazado'),
)

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    rol = models.CharField(max_length=20, choices=ROLES, default='operador')
    area_asignada = models.ForeignKey('Area', on_delete=models.SET_NULL, null=True, blank=True, related_name='miembros')
    minimo_porcentaje = models.PositiveSmallIntegerField(default=0, help_text='Porcentaje mínimo requerido')
    procesos_asignados = models.ManyToManyField('Proceso', blank=True, related_name='usuarios_asignados')
    equipo_a_cargo = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='supervisores')
    
    # Permisos
    puede_gestionar_staff = models.BooleanField(default=False)
    puede_gestionar_areas = models.BooleanField(default=False)
    puede_gestionar_procesos = models.BooleanField(default=False)
    puede_gestionar_pasos = models.BooleanField(default=False)
    puede_supervisar = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    def get_full_name(self):
        return self.user.get_full_name()
    
    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'

class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    responsable = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, related_name='areas_a_cargo')
    minimo_requerido = models.PositiveSmallIntegerField(default=0, help_text='Mínimo % requerido para el área')
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Área'
        verbose_name_plural = 'Áreas'

class Proceso(models.Model):
    nombre = models.CharField(max_length=150)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='procesos')
    objetivo = models.TextField(blank=True)
    video_ayuda = models.URLField(blank=True)
    nivel_critico = models.CharField(max_length=10, choices=CRITICIDAD, default='media')
    tiempo_estimado = models.PositiveIntegerField(null=True, blank=True, help_text='Minutos estimados')
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.area.nombre})"
    
    def get_absolute_url(self):
        return reverse('dashboard_procesos')
    
    class Meta:
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'

class Paso(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name='pasos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_PASO, default='normal')
    puntos = models.PositiveSmallIntegerField(default=1)
    orden = models.PositiveSmallIntegerField()
    ayuda_html = RichTextField(blank=True, null=True, help_text='Contenido HTML de ayuda')
    pregunta_condicion = models.CharField(max_length=255, blank=True, null=True, help_text='Pregunta si el paso es condicional')
    paso_si = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='condicion_si')
    paso_no = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='condicion_no')
    nivel_critico = models.CharField(max_length=10, choices=CRITICIDAD, default='media')
    evidencia_tipo = models.CharField(max_length=20, choices=TIPO_EVIDENCIA, default='ninguna', help_text='Tipo de evidencia requerida')
    
    def __str__(self):
        return f"{self.orden} - {self.nombre}"
    
    class Meta:
        ordering = ['orden']
        unique_together = ['proceso', 'orden']

class EjecucionProceso(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name='ejecuciones')
    usuario = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='ejecuciones')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_EJECUCION, default='en_progreso')
    puntos_obtenidos = models.PositiveSmallIntegerField(default=0)
    puntos_totales = models.PositiveSmallIntegerField(default=0)
    comentario_general = models.TextField(blank=True, help_text='Comentario de supervisión/auditoría')
    estado_supervision = models.CharField(max_length=20, choices=ESTADO_SUPERVISION, default='pendiente')
    resultado_supervision = models.CharField(max_length=20, choices=(('aprobado','Aprobado'),('rechazado','Rechazado')), null=True, blank=True)
    
    def __str__(self):
        return f"{self.proceso.nombre} - {self.usuario} - {self.estado}"
    
    def calcular_cumplimiento(self):
        if self.puntos_totales == 0:
            return 0
        return int((self.puntos_obtenidos / self.puntos_totales) * 100)

class EjecucionPaso(models.Model):
    ejecucion = models.ForeignKey(EjecucionProceso, on_delete=models.CASCADE, related_name='pasos_ejecutados')
    paso = models.ForeignKey(Paso, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=(('pendiente','Pendiente'),('completado','Completado'),('saltado','Saltado')), default='pendiente')
    respuesta_condicion = models.BooleanField(null=True, blank=True)
    evidencia_fotografica = models.ImageField(upload_to='evidencias/fotos/', blank=True, null=True)
    evidencia_descriptiva = models.TextField(blank=True)
    tiempo_inicio = models.DateTimeField(auto_now_add=True)
    tiempo_fin = models.DateTimeField(null=True, blank=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    # Campos para supervisión
    puntaje_original = models.PositiveSmallIntegerField(default=0)
    puntaje_ajustado = models.PositiveSmallIntegerField(null=True, blank=True)
    comentario_supervision = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.puntaje_original:
            self.puntaje_original = self.paso.puntos
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['paso__orden']

class Planificacion(models.Model):
    proceso = models.ForeignKey(Proceso, on_delete=models.CASCADE, related_name='planificaciones')
    frecuencia = models.CharField(max_length=10, choices=FRECUENCIA_RECURRENCIA)
    regla = models.CharField(max_length=100, help_text='Ej: "lunes,miercoles" para semanal, "15" para mensual, o "*" para diaria')
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    usuario_asignado = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='planificaciones')
    
    def __str__(self):
        return f"{self.proceso.nombre} - {self.frecuencia}"
    
    class Meta:
        verbose_name = 'Planificación'
        verbose_name_plural = 'Planificaciones'

@receiver(post_save, sender=User)
def crear_perfil_staff(sender, instance, created, **kwargs):
    if created:
        StaffProfile.objects.get_or_create(user=instance)
