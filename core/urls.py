from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo_procesos, name='home'),
    # Staff
    path('staff/crear/', views.staff_crear, name='staff_crear'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/editar/<int:pk>/', views.staff_editar, name='staff_editar'),
    path('staff/eliminar/<int:pk>/', views.staff_eliminar, name='staff_eliminar'),
    # Áreas
    path('areas/crear/', views.area_crear, name='area_crear'),
    path('areas/', views.area_dashboard, name='area_dashboard'),
    path('areas/editar/<int:pk>/', views.area_editar, name='area_editar'),
    path('areas/eliminar/<int:pk>/', views.area_eliminar, name='area_eliminar'),
    # Procesos (gestión)
    path('procesos/crear/', views.proceso_crear, name='proceso_crear'),
    path('procesos/', views.dashboard_procesos, name='dashboard_procesos'),
    path('procesos/editar/<int:pk>/', views.proceso_editar, name='proceso_editar'),
    path('procesos/eliminar/<int:pk>/', views.proceso_eliminar, name='proceso_eliminar'),
    path('procesos/visualizar/<int:pk>/', views.proceso_visualizar, name='proceso_visualizar'),
    # Pasos
    path('procesos/<int:proceso_pk>/pasos/crear/', views.paso_crear, name='paso_crear'),
    path('procesos/<int:proceso_pk>/pasos/editar/<int:paso_pk>/', views.paso_editar, name='paso_editar'),
    path('procesos/<int:proceso_pk>/pasos/eliminar/<int:paso_pk>/', views.paso_eliminar, name='paso_eliminar'),
    # Catálogo y ejecución
    path('mis-procesos/', views.catalogo_procesos, name='catalogo_procesos'),
    path('ejecutar/<int:proceso_pk>/', views.ejecutar_proceso, name='ejecutar_proceso'),
    path('mi-rendimiento/', views.rendimiento_procesos, name='rendimiento_procesos'),
    # Wiky
    path('wiky/', views.wiky, name='wiky'),
    # Login personalizado
    path('accounts/login/', views.login_view, name='login'),
    # Planificación
    path('planificacion/', views.planificacion_dashboard, name='planificacion_dashboard'),
    path('planificacion/crear/', views.planificacion_crear, name='planificacion_crear'),
    path('planificacion/editar/<int:pk>/', views.planificacion_editar, name='planificacion_editar'),
    path('planificacion/eliminar/<int:pk>/', views.planificacion_eliminar, name='planificacion_eliminar'),
    # Rendimiento de equipo
    path('rendimiento-equipo/', views.rendimiento_equipo, name='rendimiento_equipo'),
    path('detalle-mi-rendimiento/<int:ejecucion_pk>/', views.detalle_mi_rendimiento, name='detalle_mi_rendimiento'),
    path('detalle-rendimiento-equipo/<int:ejecucion_pk>/', views.detalle_rendimiento_equipo, name='detalle_rendimiento_equipo'),
    # Supervisión
    path('supervision/', views.supervision_dashboard, name='supervision_dashboard'),
    path('supervision/detalle/<int:ejecucion_pk>/', views.supervision_detalle, name='supervision_detalle'),
]