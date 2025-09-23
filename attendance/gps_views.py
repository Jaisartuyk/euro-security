"""
Vistas para el sistema de rastreo GPS en tiempo real
EURO SECURITY - GPS Tracking Views
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q, Count, Avg, Max
from django.conf import settings
from datetime import datetime, timedelta
import json

from core.permissions import employee_required
from .models_gps import WorkArea, EmployeeWorkArea, GPSTracking, LocationAlert
from .permissions import AttendancePermissions
from employees.models import Employee

@login_required
@employee_required
def real_time_tracking_dashboard(request):
    """Dashboard de rastreo en tiempo real"""
    
    # Verificar permisos - SUPERUSUARIOS: Acceso automático
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_view_location_maps(request.user):
            return render(request, 'attendance/no_permission.html', {
                'message': 'No tienes permisos para ver el rastreo GPS en tiempo real'
            })
    
    # Empleados que puede ver
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    
    # Empleados activos con ubicación reciente (últimos 30 minutos)
    thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
    active_employees = viewable_employees.filter(
        gps_tracking__timestamp__gte=thirty_minutes_ago,
        gps_tracking__is_active_session=True
    ).distinct()
    
    # Áreas de trabajo
    work_areas = WorkArea.objects.filter(is_active=True)
    
    # Alertas activas
    active_alerts = LocationAlert.objects.filter(
        employee__in=viewable_employees,
        is_resolved=False
    ).select_related('employee', 'work_area')[:10]
    
    # Estadísticas
    stats = {
        'total_employees': viewable_employees.count(),
        'active_employees': active_employees.count(),
        'total_areas': work_areas.count(),
        'active_alerts': active_alerts.count(),
    }
    
    context = {
        'stats': stats,
        'active_employees': active_employees,
        'work_areas': work_areas,
        'active_alerts': active_alerts,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'attendance/real_time_tracking.html', context)

@login_required
def gps_tracking_api(request):
    """API para obtener ubicaciones GPS en tiempo real"""
    
    # SUPERUSUARIOS: Acceso automático sin restricciones
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_view_location_maps(request.user):
            return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    # Parámetros
    minutes_ago = int(request.GET.get('minutes', 30))
    employee_id = request.GET.get('employee_id')
    
    # Filtros
    time_filter = timezone.now() - timedelta(minutes=minutes_ago)
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    
    # Query base
    tracking_query = GPSTracking.objects.filter(
        employee__in=viewable_employees,
        timestamp__gte=time_filter,
        is_active_session=True
    ).select_related('employee', 'work_area')
    
    if employee_id:
        tracking_query = tracking_query.filter(employee_id=employee_id)
    
    # Obtener última ubicación por empleado
    latest_locations = []
    for employee in viewable_employees:
        latest_tracking = tracking_query.filter(employee=employee).first()
        if latest_tracking:
            latest_locations.append({
                'employee_id': employee.id,
                'employee_name': employee.get_full_name(),
                'employee_position': employee.position.title,
                'latitude': float(latest_tracking.latitude),
                'longitude': float(latest_tracking.longitude),
                'accuracy': latest_tracking.accuracy,
                'timestamp': latest_tracking.timestamp.isoformat(),
                'work_area': {
                    'id': latest_tracking.work_area.id if latest_tracking.work_area else None,
                    'name': latest_tracking.work_area.name if latest_tracking.work_area else None,
                    'is_within': latest_tracking.is_within_work_area,
                    'distance': latest_tracking.distance_to_work_area,
                } if latest_tracking.work_area else None,
                'battery_level': latest_tracking.battery_level,
                'tracking_type': latest_tracking.get_tracking_type_display(),
            })
    
    return JsonResponse({
        'locations': latest_locations,
        'timestamp': timezone.now().isoformat(),
        'total_active': len(latest_locations)
    })

@login_required
def work_areas_api(request):
    """API para obtener áreas de trabajo"""
    
    # SUPERUSUARIOS: Acceso automático sin restricciones
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_view_location_maps(request.user):
            return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    areas = WorkArea.objects.filter(is_active=True)
    
    areas_data = []
    for area in areas:
        # Contar empleados asignados
        assigned_count = EmployeeWorkArea.objects.filter(
            work_area=area,
            is_active=True
        ).count()
        
        # Empleados actualmente en el área
        thirty_minutes_ago = timezone.now() - timedelta(minutes=30)
        current_employees = GPSTracking.objects.filter(
            work_area=area,
            is_within_work_area=True,
            timestamp__gte=thirty_minutes_ago,
            is_active_session=True
        ).count()
        
        areas_data.append({
            'id': area.id,
            'name': area.name,
            'type': area.get_area_type_display(),
            'latitude': float(area.latitude),
            'longitude': float(area.longitude),
            'radius': area.radius_meters,
            'address': area.address,
            'assigned_employees': assigned_count,
            'current_employees': current_employees,
            'requires_attendance': area.requires_attendance,
        })
    
    return JsonResponse({
        'areas': areas_data,
        'total': len(areas_data)
    })

@csrf_exempt
@login_required
@employee_required
def update_gps_location(request):
    """API para actualizar ubicación GPS del empleado"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Obtener empleado
        from core.permissions import get_employee_from_user
        employee = get_employee_from_user(request.user)
        
        # Validar datos requeridos
        required_fields = ['latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Campo requerido: {field}'}, status=400)
        
        # Crear registro de tracking
        tracking = GPSTracking.objects.create(
            employee=employee,
            latitude=data['latitude'],
            longitude=data['longitude'],
            accuracy=data.get('accuracy'),
            altitude=data.get('altitude'),
            tracking_type=data.get('tracking_type', 'AUTO'),
            battery_level=data.get('battery_level'),
            device_info=data.get('device_info', ''),
            notes=data.get('notes', ''),
        )
        
        # Verificar si está en área de trabajo
        response_data = {
            'success': True,
            'tracking_id': tracking.id,
            'timestamp': tracking.timestamp.isoformat(),
            'is_within_work_area': tracking.is_within_work_area,
            'work_area': None,
            'distance_to_area': tracking.distance_to_work_area,
        }
        
        if tracking.work_area:
            response_data['work_area'] = {
                'id': tracking.work_area.id,
                'name': tracking.work_area.name,
                'type': tracking.work_area.get_area_type_display(),
            }
        
        # Generar alertas si es necesario
        if not tracking.is_within_work_area and tracking.work_area:
            # Verificar si ya existe una alerta reciente
            recent_alert = LocationAlert.objects.filter(
                employee=employee,
                alert_type='OUT_OF_AREA',
                is_resolved=False,
                created_at__gte=timezone.now() - timedelta(minutes=15)
            ).first()
            
            if not recent_alert:
                LocationAlert.objects.create(
                    employee=employee,
                    work_area=tracking.work_area,
                    gps_tracking=tracking,
                    alert_type='OUT_OF_AREA',
                    alert_level='WARNING',
                    title=f'Empleado fuera del área: {tracking.work_area.name}',
                    message=f'{employee.get_full_name()} se encuentra a {tracking.distance_to_work_area:.0f}m del área asignada.'
                )
                response_data['alert_generated'] = True
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@employee_required
def employee_tracking_history(request, employee_id):
    """Historial de tracking de un empleado específico"""
    
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    employee = get_object_or_404(Employee, id=employee_id, id__in=viewable_employees.values_list('id', flat=True))
    
    # Filtros de fecha
    date_from = request.GET.get('date_from', timezone.now().date())
    date_to = request.GET.get('date_to', timezone.now().date())
    
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Obtener tracking del período
    tracking_records = GPSTracking.objects.filter(
        employee=employee,
        timestamp__date__range=[date_from, date_to]
    ).select_related('work_area').order_by('-timestamp')
    
    # Estadísticas del período
    stats = {
        'total_records': tracking_records.count(),
        'time_in_area': tracking_records.filter(is_within_work_area=True).count(),
        'time_out_area': tracking_records.filter(is_within_work_area=False).count(),
        'areas_visited': tracking_records.values('work_area').distinct().count(),
    }
    
    context = {
        'employee': employee,
        'tracking_records': tracking_records[:100],  # Limitar a 100 registros
        'stats': stats,
        'date_from': date_from,
        'date_to': date_to,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'attendance/employee_tracking_history.html', context)

@login_required
@employee_required
def location_alerts_view(request):
    """Vista de alertas de ubicación"""
    
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    
    # Filtros
    alert_type = request.GET.get('type', 'all')
    is_resolved = request.GET.get('resolved', 'false') == 'true'
    
    # Query base
    alerts_query = LocationAlert.objects.filter(
        employee__in=viewable_employees
    ).select_related('employee', 'work_area', 'gps_tracking')
    
    if alert_type != 'all':
        alerts_query = alerts_query.filter(alert_type=alert_type)
    
    alerts_query = alerts_query.filter(is_resolved=is_resolved)
    
    alerts = alerts_query.order_by('-created_at')[:50]
    
    # Estadísticas
    alert_stats = {
        'total_active': LocationAlert.objects.filter(
            employee__in=viewable_employees,
            is_resolved=False
        ).count(),
        'critical': LocationAlert.objects.filter(
            employee__in=viewable_employees,
            is_resolved=False,
            alert_level='CRITICAL'
        ).count(),
        'out_of_area': LocationAlert.objects.filter(
            employee__in=viewable_employees,
            is_resolved=False,
            alert_type='OUT_OF_AREA'
        ).count(),
    }
    
    context = {
        'alerts': alerts,
        'alert_stats': alert_stats,
        'alert_types': LocationAlert.ALERT_TYPES,
        'current_type': alert_type,
        'show_resolved': is_resolved,
    }
    
    return render(request, 'attendance/location_alerts.html', context)


# ==========================================
# GESTIÓN DE ÁREAS DE TRABAJO
# ==========================================

@login_required
@employee_required
def work_areas_list(request):
    """Lista de áreas de trabajo"""
    
    # Verificar permisos - SUPERUSUARIOS: Acceso automático
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_manage_work_areas(request.user):
            return render(request, 'attendance/no_permission.html', {
                'message': 'No tienes permisos para gestionar áreas de trabajo'
            })
    
    work_areas = WorkArea.objects.all().order_by('name')
    
    # Estadísticas
    stats = {
        'total_areas': work_areas.count(),
        'active_areas': work_areas.filter(is_active=True).count(),
        'total_assignments': EmployeeWorkArea.objects.filter(is_active=True).count(),
    }
    
    context = {
        'work_areas': work_areas,
        'stats': stats,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'attendance/work_areas_list.html', context)


@login_required
@employee_required
def work_area_create(request):
    """Crear nueva área de trabajo"""
    
    # Verificar permisos
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_manage_work_areas(request.user):
            return render(request, 'attendance/no_permission.html', {
                'message': 'No tienes permisos para crear áreas de trabajo'
            })
    
    if request.method == 'POST':
        try:
            # Crear área de trabajo
            work_area = WorkArea.objects.create(
                name=request.POST['name'],
                description=request.POST.get('description', ''),
                area_type=request.POST['area_type'],
                latitude=request.POST['latitude'],
                longitude=request.POST['longitude'],
                radius_meters=request.POST.get('radius_meters', 50),
                address=request.POST.get('address', ''),
                contact_person=request.POST.get('contact_person', ''),
                contact_phone=request.POST.get('contact_phone', ''),
                start_time=request.POST.get('start_time') or None,
                end_time=request.POST.get('end_time') or None,
                requires_attendance=request.POST.get('requires_attendance') == 'on',
                is_active=True,
                created_by=request.user
            )
            
            messages.success(request, f'Área de trabajo "{work_area.name}" creada exitosamente.')
            return redirect('attendance:work_areas_list')
            
        except Exception as e:
            messages.error(request, f'Error al crear área de trabajo: {str(e)}')
    
    context = {
        'area_types': WorkArea.AREA_TYPES,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'attendance/work_area_create.html', context)


@login_required
@employee_required
def work_area_detail(request, pk):
    """Detalle de área de trabajo"""
    
    work_area = get_object_or_404(WorkArea, pk=pk)
    
    # Empleados asignados
    assignments = EmployeeWorkArea.objects.filter(
        work_area=work_area,
        is_active=True
    ).select_related('employee')
    
    # Tracking reciente
    recent_tracking = GPSTracking.objects.filter(
        work_area=work_area,
        timestamp__gte=timezone.now() - timedelta(hours=24)
    ).select_related('employee').order_by('-timestamp')[:10]
    
    # Estadísticas
    stats = {
        'assigned_employees': assignments.count(),
        'recent_visits': recent_tracking.count(),
        'employees_in_area': GPSTracking.objects.filter(
            work_area=work_area,
            is_within_work_area=True,
            timestamp__gte=timezone.now() - timedelta(minutes=30)
        ).values('employee').distinct().count(),
    }
    
    # Configuración para JavaScript
    work_area_config = {
        'name': work_area.name,
        'latitude': str(work_area.latitude),
        'longitude': str(work_area.longitude),
        'radius_meters': work_area.radius_meters,
        'area_type': work_area.get_area_type_display(),
        'address': work_area.address or '',
    }
    
    context = {
        'work_area': work_area,
        'assignments': assignments,
        'recent_tracking': recent_tracking,
        'stats': stats,
        'work_area_config': work_area_config,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'attendance/work_area_detail.html', context)


@login_required
@employee_required
def work_area_edit(request, pk):
    """Editar área de trabajo"""
    
    work_area = get_object_or_404(WorkArea, pk=pk)
    
    # Verificar permisos
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_manage_work_areas(request.user):
            return render(request, 'attendance/no_permission.html', {
                'message': 'No tienes permisos para editar áreas de trabajo'
            })
    
    if request.method == 'POST':
        try:
            # Actualizar área de trabajo
            work_area.name = request.POST['name']
            work_area.description = request.POST.get('description', '')
            work_area.area_type = request.POST['area_type']
            work_area.latitude = request.POST['latitude']
            work_area.longitude = request.POST['longitude']
            work_area.radius_meters = request.POST.get('radius_meters', 50)
            work_area.address = request.POST.get('address', '')
            work_area.contact_person = request.POST.get('contact_person', '')
            work_area.contact_phone = request.POST.get('contact_phone', '')
            work_area.start_time = request.POST.get('start_time') or None
            work_area.end_time = request.POST.get('end_time') or None
            work_area.requires_attendance = request.POST.get('requires_attendance') == 'on'
            work_area.is_active = request.POST.get('is_active') == 'on'
            work_area.updated_by = request.user
            work_area.save()
            
            messages.success(request, f'Área de trabajo "{work_area.name}" actualizada exitosamente.')
            return redirect('attendance:work_area_detail', pk=work_area.pk)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar área de trabajo: {str(e)}')
    
    # Configuración para JavaScript
    work_area_config = {
        'name': work_area.name,
        'latitude': str(work_area.latitude),
        'longitude': str(work_area.longitude),
        'radius_meters': work_area.radius_meters,
        'area_type': work_area.get_area_type_display(),
        'address': work_area.address or '',
    }
    
    context = {
        'work_area': work_area,
        'area_types': WorkArea.AREA_TYPES,
        'work_area_config': work_area_config,
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    
    return render(request, 'attendance/work_area_edit.html', context)


@login_required
@employee_required
def work_area_assign_employees(request, pk):
    """Asignar empleados a área de trabajo"""
    
    work_area = get_object_or_404(WorkArea, pk=pk)
    
    # Verificar permisos
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_manage_work_areas(request.user):
            return render(request, 'attendance/no_permission.html', {
                'message': 'No tienes permisos para asignar empleados'
            })
    
    if request.method == 'POST':
        try:
            employee_ids = request.POST.getlist('employees')
            
            # Desactivar asignaciones existentes si se solicita
            if request.POST.get('replace_existing') == 'on':
                EmployeeWorkArea.objects.filter(work_area=work_area).update(is_active=False)
            
            # Crear nuevas asignaciones
            created_count = 0
            for employee_id in employee_ids:
                employee = Employee.objects.get(id=employee_id)
                assignment, created = EmployeeWorkArea.objects.get_or_create(
                    employee=employee,
                    work_area=work_area,
                    defaults={
                        'is_primary': request.POST.get(f'primary_{employee_id}') == 'on',
                        'is_active': True,
                    }
                )
                if created:
                    created_count += 1
                elif not assignment.is_active:
                    assignment.is_active = True
                    assignment.save()
                    created_count += 1
            
            messages.success(request, f'{created_count} empleados asignados al área "{work_area.name}".')
            return redirect('attendance:work_area_detail', pk=work_area.pk)
            
        except Exception as e:
            messages.error(request, f'Error al asignar empleados: {str(e)}')
    
    # Empleados disponibles
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    assigned_employees = EmployeeWorkArea.objects.filter(
        work_area=work_area,
        is_active=True
    ).values_list('employee_id', flat=True)
    
    available_employees = viewable_employees.exclude(id__in=assigned_employees)
    current_assignments = EmployeeWorkArea.objects.filter(
        work_area=work_area,
        is_active=True
    ).select_related('employee')
    
    context = {
        'work_area': work_area,
        'available_employees': available_employees,
        'current_assignments': current_assignments,
    }
    
    return render(request, 'attendance/work_area_assign_employees.html', context)
