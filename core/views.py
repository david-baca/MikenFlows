from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .models import *
from .forms import *

# ---------- Helpers de permisos ----------
def es_admin(user):
    return hasattr(user, 'staff_profile') and user.staff_profile.rol == 'admin'

def puede_gestionar_staff(user):
    return es_admin(user) or (hasattr(user, 'staff_profile') and user.staff_profile.puede_gestionar_staff)

def puede_gestionar_areas(user):
    return es_admin(user) or (hasattr(user, 'staff_profile') and user.staff_profile.puede_gestionar_areas)

def puede_gestionar_procesos(user):
    return es_admin(user) or (hasattr(user, 'staff_profile') and user.staff_profile.puede_gestionar_procesos)

def puede_gestionar_pasos(user):
    return es_admin(user) or (hasattr(user, 'staff_profile') and user.staff_profile.puede_gestionar_pasos)

def puede_supervisar(user):
    return es_admin(user) or (hasattr(user, 'staff_profile') and (user.staff_profile.puede_supervisar or user.staff_profile.rol in ['supervisor','auditor']))

# ---------- VISTAS DE STAFF (MOD-1) ----------
@login_required
@user_passes_test(puede_gestionar_staff)
def staff_crear(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe')
            else:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
                staff = form.save(commit=False)
                staff.user = user
                staff.save()
                form.save_m2m()
                messages.success(request, 'Staff creado correctamente')
                return redirect('staff_dashboard')
    else:
        form = StaffForm()
    return render(request, 'core/staff_form.html', {'form': form, 'titulo': 'Crear Staff'})

@login_required
@user_passes_test(puede_gestionar_staff)
def staff_dashboard(request):
    q = request.GET.get('q', '')
    area_id = request.GET.get('area', '')
    rol = request.GET.get('rol', '')
    staff_list = StaffProfile.objects.select_related('user', 'area_asignada').all()
    if q:
        staff_list = staff_list.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(user__username__icontains=q))
    if area_id:
        staff_list = staff_list.filter(area_asignada_id=area_id)
    if rol:
        staff_list = staff_list.filter(rol=rol)
    paginator = Paginator(staff_list, 10)
    page = request.GET.get('page')
    staff_page = paginator.get_page(page)
    areas = Area.objects.all()
    roles = ROLES
    return render(request, 'core/staff_dashboard.html', {'staff_list': staff_page, 'areas': areas, 'roles': roles, 'filtros': {'q': q, 'area': area_id, 'rol': rol}})

@login_required
@user_passes_test(puede_gestionar_staff)
def staff_editar(request, pk):
    staff = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            user = staff.user
            user.username = form.cleaned_data['username']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
            user.save()
            form.save()
            messages.success(request, 'Staff actualizado')
            return redirect('staff_dashboard')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'core/staff_form.html', {'form': form, 'titulo': 'Editar Staff'})

@login_required
@user_passes_test(puede_gestionar_staff)
def staff_eliminar(request, pk):
    staff = get_object_or_404(StaffProfile, pk=pk)
    if request.method == 'POST':
        staff.user.delete()
        staff.delete()
        messages.success(request, 'Staff eliminado')
        return redirect('staff_dashboard')
    return render(request, 'core/confirm_delete.html', {'object': staff, 'tipo': 'Staff', 'cancel_url': 'staff_dashboard'})

# ---------- VISTAS DE ÁREAS (MOD-2) ----------
@login_required
@user_passes_test(puede_gestionar_areas)
def area_crear(request):
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área creada')
            return redirect('area_dashboard')
    else:
        form = AreaForm()
    return render(request, 'core/area_form.html', {'form': form, 'titulo': 'Crear Área'})

@login_required
@user_passes_test(puede_gestionar_areas)
def area_dashboard(request):
    q = request.GET.get('q', '')
    responsable_id = request.GET.get('responsable', '')
    areas = Area.objects.select_related('responsable').all()
    if q:
        areas = areas.filter(nombre__icontains=q)
    if responsable_id:
        areas = areas.filter(responsable_id=responsable_id)
    paginator = Paginator(areas, 10)
    page = request.GET.get('page')
    areas_page = paginator.get_page(page)
    responsables = StaffProfile.objects.filter(rol='supervisor')
    return render(request, 'core/area_dashboard.html', {'areas': areas_page, 'responsables': responsables, 'filtros': {'q': q, 'responsable': responsable_id}})

@login_required
@user_passes_test(puede_gestionar_areas)
def area_editar(request, pk):
    area = get_object_or_404(Area, pk=pk)
    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área actualizada')
            return redirect('area_dashboard')
    else:
        form = AreaForm(instance=area)
    return render(request, 'core/area_form.html', {'form': form, 'titulo': 'Editar Área'})

@login_required
@user_passes_test(puede_gestionar_areas)
def area_eliminar(request, pk):
    area = get_object_or_404(Area, pk=pk)
    if request.method == 'POST':
        area.delete()
        messages.success(request, 'Área eliminada')
        return redirect('area_dashboard')
    return render(request, 'core/confirm_delete.html', {'object': area, 'tipo': 'Área', 'cancel_url': 'area_dashboard'})

# ---------- VISTAS DE PROCESOS (MOD-3) ----------
@login_required
@user_passes_test(puede_gestionar_procesos)
def proceso_crear(request):
    if request.method == 'POST':
        form = ProcesoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proceso creado')
            return redirect('dashboard_procesos')
    else:
        form = ProcesoForm()
    return render(request, 'core/proceso_form.html', {'form': form, 'titulo': 'Crear Proceso'})

@login_required
@user_passes_test(puede_gestionar_procesos)
def dashboard_procesos(request):
    q = request.GET.get('q', '')
    area_id = request.GET.get('area', '')
    procesos = Proceso.objects.select_related('area').all()
    if q:
        procesos = procesos.filter(nombre__icontains=q)
    if area_id:
        procesos = procesos.filter(area_id=area_id)
    paginator = Paginator(procesos, 10)
    page = request.GET.get('page')
    procesos_page = paginator.get_page(page)
    areas = Area.objects.all()
    return render(request, 'core/proceso_dashboard.html', {'procesos': procesos_page, 'areas': areas, 'filtros': {'q': q, 'area': area_id}})

@login_required
@user_passes_test(puede_gestionar_procesos)
def proceso_editar(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    if request.method == 'POST':
        form = ProcesoForm(request.POST, instance=proceso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proceso actualizado')
            return redirect('dashboard_procesos')
    else:
        form = ProcesoForm(instance=proceso)
    return render(request, 'core/proceso_form.html', {'form': form, 'titulo': 'Editar Proceso'})

@login_required
@user_passes_test(puede_gestionar_procesos)
def proceso_eliminar(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    if request.method == 'POST':
        proceso.delete()
        messages.success(request, 'Proceso eliminado')
        return redirect('dashboard_procesos')
    return render(request, 'core/confirm_delete.html', {'object': proceso, 'tipo': 'Proceso', 'cancel_url': 'dashboard_procesos'})

@login_required
def proceso_visualizar(request, pk):
    proceso = get_object_or_404(Proceso, pk=pk)
    pasos = proceso.pasos.all()
    nombre_paso = request.GET.get('nombre_paso', '')
    tipo_paso = request.GET.get('tipo_paso', '')
    if nombre_paso:
        pasos = pasos.filter(nombre__icontains=nombre_paso)
    if tipo_paso:
        pasos = pasos.filter(tipo=tipo_paso)
    paginator = Paginator(pasos, 10)
    page = request.GET.get('page')
    pasos_page = paginator.get_page(page)
    return render(request, 'core/proceso_detalle.html', {'proceso': proceso, 'pasos': pasos_page, 'filtros': {'nombre_paso': nombre_paso, 'tipo_paso': tipo_paso}})

# ---------- VISTAS DE PASOS ----------
@login_required
@user_passes_test(puede_gestionar_pasos)
def paso_crear(request, proceso_pk):
    proceso = get_object_or_404(Proceso, pk=proceso_pk)
    if request.method == 'POST':
        form = PasoForm(request.POST, proceso_id=proceso.pk)
        if form.is_valid():
            paso = form.save(commit=False)
            paso.proceso = proceso
            paso.save()
            messages.success(request, 'Paso creado correctamente')
            return redirect('proceso_visualizar', pk=proceso.pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error en {field}: {error}')
    else:
        form = PasoForm(proceso_id=proceso.pk)
    return render(request, 'core/paso_form.html', {'form': form, 'proceso': proceso, 'titulo': 'Crear Paso'})

@login_required
@user_passes_test(puede_gestionar_pasos)
def paso_editar(request, proceso_pk, paso_pk):
    proceso = get_object_or_404(Proceso, pk=proceso_pk)
    paso = get_object_or_404(Paso, pk=paso_pk, proceso=proceso)
    if request.method == 'POST':
        form = PasoForm(request.POST, instance=paso, proceso_id=proceso.pk)
        if form.is_valid():
            form.save()
            messages.success(request, 'Paso actualizado')
            return redirect('proceso_visualizar', pk=proceso.pk)
    else:
        form = PasoForm(instance=paso, proceso_id=proceso.pk)
    return render(request, 'core/paso_form.html', {'form': form, 'proceso': proceso, 'titulo': 'Editar Paso'})

@login_required
@user_passes_test(puede_gestionar_pasos)
def paso_eliminar(request, proceso_pk, paso_pk):
    proceso = get_object_or_404(Proceso, pk=proceso_pk)
    paso = get_object_or_404(Paso, pk=paso_pk, proceso=proceso)
    if request.method == 'POST':
        paso.delete()
        messages.success(request, 'Paso eliminado')
        return redirect('proceso_visualizar', pk=proceso.pk)
    return render(request, 'core/confirm_delete.html', {'object': paso, 'tipo': 'Paso', 'cancel_url': reverse('proceso_visualizar', args=[proceso.pk])})

# ---------- CATÁLOGO Y EJECUCIÓN ----------
@login_required
def catalogo_procesos(request):
    q = request.GET.get('q', '')
    staff = request.user.staff_profile
    if staff.rol == 'operador':
        procesos = staff.procesos_asignados.filter(activo=True)
    else:
        procesos = Proceso.objects.filter(activo=True)
    if q:
        procesos = procesos.filter(nombre__icontains=q)
    paginator = Paginator(procesos, 10)
    page = request.GET.get('page')
    procesos_page = paginator.get_page(page)
    return render(request, 'core/catalogo_procesos.html', {'procesos': procesos_page, 'filtros': {'q': q}})

@login_required
def ejecutar_proceso(request, proceso_pk):
    proceso = get_object_or_404(Proceso, pk=proceso_pk, activo=True)
    ejecucion, created = EjecucionProceso.objects.get_or_create(
        proceso=proceso,
        usuario=request.user.staff_profile,
        estado='en_progreso',
        defaults={'puntos_totales': sum(p.puntos for p in proceso.pasos.all())}
    )
    pasos_ejecutados_ids = ejecucion.pasos_ejecutados.filter(estado='completado').values_list('paso_id', flat=True)
    siguiente_paso = proceso.pasos.exclude(id__in=pasos_ejecutados_ids).first()
    
    if not siguiente_paso:
        ejecucion.estado = 'completado'
        ejecucion.fecha_fin = timezone.now()
        ejecucion.save()
        return redirect('rendimiento_procesos')
    
    if request.method == 'POST' and 'respuesta_condicion' in request.POST:
        respuesta = request.POST.get('respuesta_condicion') == 'si'
        ejec_paso, _ = EjecucionPaso.objects.get_or_create(ejecucion=ejecucion, paso=siguiente_paso)
        ejec_paso.estado = 'completado'
        ejec_paso.respuesta_condicion = respuesta
        ejec_paso.fecha_completado = timezone.now()
        ejec_paso.tiempo_fin = timezone.now()
        # Guardar evidencias
        if 'evidencia_fotografica' in request.FILES:
            ejec_paso.evidencia_fotografica = request.FILES['evidencia_fotografica']
        if 'evidencia_descriptiva' in request.POST:
            ejec_paso.evidencia_descriptiva = request.POST['evidencia_descriptiva']
        ejec_paso.save()
        if respuesta:
            ejecucion.puntos_obtenidos += siguiente_paso.puntos
        # Lógica de saltos condicionales
        if respuesta and siguiente_paso.paso_si:
            pasos_intermedios = proceso.pasos.filter(orden__gt=siguiente_paso.orden, orden__lt=siguiente_paso.paso_si.orden)
            for p in pasos_intermedios:
                EjecucionPaso.objects.get_or_create(ejecucion=ejecucion, paso=p, defaults={'estado': 'saltado'})
        elif not respuesta and siguiente_paso.paso_no:
            pasos_intermedios = proceso.pasos.filter(orden__gt=siguiente_paso.orden, orden__lt=siguiente_paso.paso_no.orden)
            for p in pasos_intermedios:
                EjecucionPaso.objects.get_or_create(ejecucion=ejecucion, paso=p, defaults={'estado': 'saltado'})
        ejecucion.save()
        return redirect('ejecutar_proceso', proceso_pk=proceso.pk)
    
    return render(request, 'core/ejecutar_paso.html', {
        'proceso': proceso,
        'paso': siguiente_paso,
        'ejecucion': ejecucion,
        'evidencia_tipo': siguiente_paso.evidencia_tipo,
    })

# ---------- RENDIMIENTO (MOD-5) ----------
@login_required
def rendimiento_procesos(request):
    ejecuciones = EjecucionProceso.objects.filter(usuario=request.user.staff_profile).order_by('-fecha_inicio')
    fecha = request.GET.get('fecha', '')
    estado = request.GET.get('estado', '')
    if fecha:
        ejecuciones = ejecuciones.filter(fecha_inicio__date=fecha)
    if estado:
        ejecuciones = ejecuciones.filter(estado=estado)
    paginator = Paginator(ejecuciones, 10)
    page = request.GET.get('page')
    ejecuciones_page = paginator.get_page(page)
    return render(request, 'core/rendimiento.html', {'ejecuciones': ejecuciones_page, 'filtros': {'fecha': fecha, 'estado': estado}})

@login_required
def detalle_mi_rendimiento(request, ejecucion_pk):
    ejecucion = get_object_or_404(EjecucionProceso, pk=ejecucion_pk, usuario=request.user.staff_profile)
    pasos = ejecucion.pasos_ejecutados.all().select_related('paso')
    return render(request, 'core/detalle_rendimiento.html', {'ejecucion': ejecucion, 'pasos': pasos})

@login_required
def rendimiento_equipo(request):
    if not puede_supervisar(request.user):
        messages.error(request, 'No tienes permiso para ver el rendimiento del equipo')
        return redirect('rendimiento_procesos')
    staff = request.user.staff_profile
    equipo_ids = staff.equipo_a_cargo.values_list('id', flat=True)
    ejecuciones = EjecucionProceso.objects.filter(usuario_id__in=equipo_ids).order_by('-fecha_inicio')
    fecha = request.GET.get('fecha', '')
    estado = request.GET.get('estado', '')
    usuario_id = request.GET.get('usuario', '')
    if fecha:
        ejecuciones = ejecuciones.filter(fecha_inicio__date=fecha)
    if estado:
        ejecuciones = ejecuciones.filter(estado=estado)
    if usuario_id:
        ejecuciones = ejecuciones.filter(usuario_id=usuario_id)
    paginator = Paginator(ejecuciones, 10)
    page = request.GET.get('page')
    ejecuciones_page = paginator.get_page(page)
    usuarios = StaffProfile.objects.filter(id__in=equipo_ids)
    return render(request, 'core/rendimiento_equipo.html', {'ejecuciones': ejecuciones_page, 'usuarios': usuarios, 'filtros': {'fecha': fecha, 'estado': estado, 'usuario': usuario_id}})

@login_required
def detalle_rendimiento_equipo(request, ejecucion_pk):
    ejecucion = get_object_or_404(EjecucionProceso, pk=ejecucion_pk)
    # Verificar que el usuario logueado tenga a cargo al dueño de la ejecución
    if not puede_supervisar(request.user) and request.user.staff_profile != ejecucion.usuario:
        messages.error(request, 'No tienes permiso para ver esta ejecución')
        return redirect('rendimiento_equipo')
    pasos = ejecucion.pasos_ejecutados.all().select_related('paso')
    return render(request, 'core/detalle_rendimiento_equipo.html', {'ejecucion': ejecucion, 'pasos': pasos})

# ---------- SUPERVISIÓN (MOD-7) ----------
@login_required
@user_passes_test(puede_supervisar)
def supervision_dashboard(request):
    # Procesos que están en estado 'completado' o 'en_progreso' y pendientes de supervisión
    # o que ya tienen supervisión pero no finalizada
    staff = request.user.staff_profile
    equipo_ids = staff.equipo_a_cargo.values_list('id', flat=True)
    supervisiones = EjecucionProceso.objects.filter(usuario_id__in=equipo_ids, estado__in=['completado', 'en_progreso']).exclude(estado_supervision='aprobado').order_by('-fecha_inicio')
    usuario = request.GET.get('usuario', '')
    proceso = request.GET.get('proceso', '')
    estado_sup = request.GET.get('estado_sup', '')
    if usuario:
        supervisiones = supervisiones.filter(usuario_id=usuario)
    if proceso:
        supervisiones = supervisiones.filter(proceso_id=proceso)
    if estado_sup:
        supervisiones = supervisiones.filter(estado_supervision=estado_sup)
    paginator = Paginator(supervisiones, 10)
    page = request.GET.get('page')
    supervisiones_page = paginator.get_page(page)
    usuarios = StaffProfile.objects.filter(id__in=equipo_ids)
    procesos_list = Proceso.objects.filter(id__in=supervisiones.values_list('proceso_id', flat=True))
    return render(request, 'core/supervision_dashboard.html', {
        'supervisiones': supervisiones_page,
        'usuarios': usuarios,
        'procesos': procesos_list,
        'filtros': {'usuario': usuario, 'proceso': proceso, 'estado_sup': estado_sup}
    })

@login_required
@user_passes_test(puede_supervisar)
def supervision_detalle(request, ejecucion_pk):
    ejecucion = get_object_or_404(EjecucionProceso, pk=ejecucion_pk)
    # Verificar que el supervisor tenga al usuario a cargo
    if request.user.staff_profile not in ejecucion.usuario.supervisores.all() and not es_admin(request.user):
        messages.error(request, 'No puedes supervisar este proceso')
        return redirect('supervision_dashboard')
    
    pasos = ejecucion.pasos_ejecutados.all().select_related('paso')
    if request.method == 'POST':
        # Guardar ajustes de pasos
        for paso_ejec in pasos:
            puntaje_ajustado = request.POST.get(f'puntaje_ajustado_{paso_ejec.id}')
            comentario = request.POST.get(f'comentario_supervision_{paso_ejec.id}')
            if puntaje_ajustado is not None:
                paso_ejec.puntaje_ajustado = int(puntaje_ajustado) if puntaje_ajustado else None
            paso_ejec.comentario_supervision = comentario or ''
            paso_ejec.save()
        # Guardar comentario general y resultado
        ejecucion.comentario_general = request.POST.get('comentario_general', '')
        if 'aprobar' in request.POST:
            ejecucion.resultado_supervision = 'aprobado'
            ejecucion.estado_supervision = 'aprobado'
            ejecucion.estado = 'supervisado'
            messages.success(request, 'Proceso aprobado')
        elif 'rechazar' in request.POST:
            ejecucion.resultado_supervision = 'rechazado'
            ejecucion.estado_supervision = 'rechazado'
            ejecucion.estado = 'supervisado'
            messages.success(request, 'Proceso rechazado')
        else:
            ejecucion.estado_supervision = 'en_revision'
            messages.success(request, 'Cambios guardados')
        ejecucion.save()
        return redirect('supervision_dashboard')
    
    return render(request, 'core/supervision_detalle.html', {'ejecucion': ejecucion, 'pasos': pasos})

# ---------- PLANIFICACIÓN (MOD-6) ----------
@login_required
@user_passes_test(puede_gestionar_procesos)
def planificacion_dashboard(request):
    planificaciones = Planificacion.objects.all().select_related('proceso', 'usuario_asignado')
    proceso_id = request.GET.get('proceso', '')
    frecuencia = request.GET.get('frecuencia', '')
    estado = request.GET.get('estado', '')
    if proceso_id:
        planificaciones = planificaciones.filter(proceso_id=proceso_id)
    if frecuencia:
        planificaciones = planificaciones.filter(frecuencia=frecuencia)
    if estado:
        planificaciones = planificaciones.filter(activo=(estado == 'activo'))
    paginator = Paginator(planificaciones, 10)
    page = request.GET.get('page')
    planificaciones_page = paginator.get_page(page)
    procesos = Proceso.objects.all()
    return render(request, 'core/planificacion_dashboard.html', {
        'planificaciones': planificaciones_page,
        'procesos': procesos,
        'filtros': {'proceso': proceso_id, 'frecuencia': frecuencia, 'estado': estado}
    })

@login_required
@user_passes_test(puede_gestionar_procesos)
def planificacion_crear(request):
    if request.method == 'POST':
        form = PlanificacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Planificación creada')
            return redirect('planificacion_dashboard')
    else:
        form = PlanificacionForm(initial={'usuario_asignado': request.user.staff_profile})
    return render(request, 'core/planificacion_form.html', {'form': form, 'titulo': 'Crear Planificación'})

@login_required
@user_passes_test(puede_gestionar_procesos)
def planificacion_editar(request, pk):
    plan = get_object_or_404(Planificacion, pk=pk)
    if request.method == 'POST':
        form = PlanificacionForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Planificación actualizada')
            return redirect('planificacion_dashboard')
    else:
        form = PlanificacionForm(instance=plan)
    return render(request, 'core/planificacion_form.html', {'form': form, 'titulo': 'Editar Planificación'})

@login_required
@user_passes_test(puede_gestionar_procesos)
def planificacion_eliminar(request, pk):
    plan = get_object_or_404(Planificacion, pk=pk)
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Planificación eliminada')
        return redirect('planificacion_dashboard')
    return render(request, 'core/confirm_delete.html', {'object': plan, 'tipo': 'Planificación', 'cancel_url': 'planificacion_dashboard'})

# ---------- WIKY (MOD-4) ----------
@login_required
def wiky(request):
    areas = Area.objects.prefetch_related('procesos__pasos').all()
    return render(request, 'core/wiky.html', {'areas': areas})

# ---------- LOGIN ----------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('catalogo_procesos')
        else:
            messages.error(request, 'Credenciales inválidas')
    return render(request, 'registration/login.html')
