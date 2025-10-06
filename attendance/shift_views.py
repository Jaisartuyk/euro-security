"""
Vistas para la gestión de turnos y horarios de trabajo
EURO SECURITY - Sistema de Turnos Profesional
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import json

from core.permissions import employee_required, permission_required
from .models import ShiftTemplate, WorkSchedule, Shift, EmployeeShiftAssignment
from employees.models import Employee


@login_required
@permission_required('supervisor')
def shift_management_dashboard(request):
    """
    Dashboard principal para gestión de turnos
    """
    
    # Estadísticas generales
    stats = {
        'total_templates': ShiftTemplate.objects.filter(is_active=True).count(),
        'active_schedules': WorkSchedule.objects.filter(is_active=True).count(),
        'total_assignments': EmployeeShiftAssignment.objects.filter(status='ACTIVE').count(),
        'employees_with_shifts': Employee.objects.filter(
            shift_assignments__status='ACTIVE'
        ).distinct().count(),
    }
    
    # Plantillas más usadas
    popular_templates = ShiftTemplate.objects.filter(
        is_active=True,
        work_schedules__is_active=True
    ).annotate(
        usage_count=Count('work_schedules')
    ).order_by('-usage_count')[:5]
    
    # Horarios activos recientes
    recent_schedules = WorkSchedule.objects.filter(
        is_active=True
    ).select_related('shift_template').order_by('-created_at')[:10]
    
    # Asignaciones pendientes
    pending_assignments = EmployeeShiftAssignment.objects.filter(
        status='PENDING'
    ).select_related('employee', 'shift__work_schedule').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'popular_templates': popular_templates,
        'recent_schedules': recent_schedules,
        'pending_assignments': pending_assignments,
        'page_title': 'Gestión de Turnos',
        'breadcrumb': [
            {'name': 'Inicio', 'url': '/'},
            {'name': 'Asistencia', 'url': '/asistencia/'},
            {'name': 'Gestión de Turnos', 'url': ''}
        ]
    }
    
    return render(request, 'attendance/shifts/dashboard.html', context)


@login_required
@permission_required('supervisor')
def shift_templates_list(request):
    """
    Lista de plantillas de turnos disponibles
    """
    
    # Filtros
    category = request.GET.get('category', '')
    shift_type = request.GET.get('shift_type', '')
    search = request.GET.get('search', '')
    
    # Query base
    templates = ShiftTemplate.objects.filter(is_active=True)
    
    # Aplicar filtros
    if category:
        templates = templates.filter(category=category)
    if shift_type:
        templates = templates.filter(shift_type=shift_type)
    if search:
        templates = templates.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Ordenar
    templates = templates.order_by('category', 'name')
    
    # Paginación
    paginator = Paginator(templates, 12)  # 12 plantillas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    categories = ShiftTemplate.TEMPLATE_CATEGORIES
    shift_types = ShiftTemplate.SHIFT_TYPES
    
    context = {
        'page_obj': page_obj,
        'templates': page_obj.object_list,
        'categories': categories,
        'shift_types': shift_types,
        'current_category': category,
        'current_shift_type': shift_type,
        'current_search': search,
        'page_title': 'Plantillas de Turnos',
        'breadcrumb': [
            {'name': 'Inicio', 'url': '/'},
            {'name': 'Asistencia', 'url': '/asistencia/'},
            {'name': 'Gestión de Turnos', 'url': '/asistencia/turnos/'},
            {'name': 'Plantillas', 'url': ''}
        ]
    }
    
    return render(request, 'attendance/shifts/templates_list.html', context)


@login_required
@permission_required('supervisor')
def shift_template_detail(request, template_id):
    """
    Detalle de una plantilla de turno
    """
    
    template = get_object_or_404(ShiftTemplate, id=template_id, is_active=True)
    
    # Configuración de turnos
    shifts_config = template.get_shifts_config_list()
    
    # Horarios que usan esta plantilla
    work_schedules = WorkSchedule.objects.filter(
        shift_template=template,
        is_active=True
    ).order_by('-created_at')
    
    # Estadísticas de uso
    usage_stats = {
        'total_schedules': work_schedules.count(),
        'active_assignments': EmployeeShiftAssignment.objects.filter(
            shift__work_schedule__shift_template=template,
            status='ACTIVE'
        ).count(),
        'employees_count': Employee.objects.filter(
            shift_assignments__shift__work_schedule__shift_template=template,
            shift_assignments__status='ACTIVE'
        ).distinct().count()
    }
    
    context = {
        'template': template,
        'shifts_config': shifts_config,
        'work_schedules': work_schedules,
        'usage_stats': usage_stats,
        'page_title': f'Plantilla: {template.name}',
        'breadcrumb': [
            {'name': 'Inicio', 'url': '/'},
            {'name': 'Asistencia', 'url': '/asistencia/'},
            {'name': 'Gestión de Turnos', 'url': '/asistencia/turnos/'},
            {'name': 'Plantillas', 'url': '/asistencia/turnos/plantillas/'},
            {'name': template.name, 'url': ''}
        ]
    }
    
    return render(request, 'attendance/shifts/template_detail.html', context)


@login_required
@permission_required('management')
def create_work_schedule(request, template_id=None):
    """
    Crear un nuevo horario de trabajo basado en una plantilla
    """
    
    template = None
    if template_id:
        template = get_object_or_404(ShiftTemplate, id=template_id, is_active=True)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            # Crear horario de trabajo
            work_schedule = WorkSchedule.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                schedule_type=data['schedule_type'],
                shift_template_id=data['template_id'],
                start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
                end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
                overtime_threshold_daily=float(data.get('overtime_threshold_daily', 8.0)),
                overtime_threshold_weekly=float(data.get('overtime_threshold_weekly', 40.0)),
                night_shift_start=datetime.strptime(data.get('night_shift_start', '22:00'), '%H:%M').time(),
                night_shift_end=datetime.strptime(data.get('night_shift_end', '06:00'), '%H:%M').time(),
                night_shift_multiplier=float(data.get('night_shift_multiplier', 1.25)),
                break_duration_minutes=int(data.get('break_duration_minutes', 60)),
                paid_break_minutes=int(data.get('paid_break_minutes', 15)),
                created_by=request.user
            )
            
            # Crear turnos basados en la plantilla
            shifts_config = work_schedule.shift_template.get_shifts_config_list()
            for i, shift_data in enumerate(shifts_config):
                Shift.objects.create(
                    work_schedule=work_schedule,
                    name=shift_data['name'],
                    custom_name=shift_data.get('custom_name', ''),
                    start_time=datetime.strptime(shift_data['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(shift_data['end_time'], '%H:%M').time(),
                    is_overnight=shift_data.get('is_overnight', False),
                    color=shift_data.get('color', '#3b82f6'),
                    icon=shift_data.get('icon', 'fas fa-clock'),
                    order=i + 1
                )
            
            messages.success(request, f'Horario "{work_schedule.name}" creado exitosamente.')
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Horario creado exitosamente',
                    'schedule_id': work_schedule.id,
                    'redirect_url': f'/asistencia/turnos/horarios/{work_schedule.id}/'
                })
            
            return redirect('attendance:work_schedules_list')
            
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)
            
            messages.error(request, f'Error al crear horario: {str(e)}')
    
    # GET request - mostrar formulario
    templates = ShiftTemplate.objects.filter(is_active=True).order_by('category', 'name')
    
    context = {
        'template': template,
        'templates': templates,
        'schedule_types': WorkSchedule.SCHEDULE_TYPES,
        'page_title': 'Crear Horario de Trabajo',
        'breadcrumb': [
            {'name': 'Inicio', 'url': '/'},
            {'name': 'Asistencia', 'url': '/asistencia/'},
            {'name': 'Gestión de Turnos', 'url': '/asistencia/turnos/'},
            {'name': 'Crear Horario', 'url': ''}
        ]
    }
    
    return render(request, 'attendance/shifts/create_schedule.html', context)


@login_required
@permission_required('supervisor')
def work_schedules_list(request, show_assignment=False):
    """
    Lista de horarios de trabajo con opción de mostrar modal de asignación
    """
    
    # Filtros
    schedule_type = request.GET.get('schedule_type', '')
    template_id = request.GET.get('template', '')
    search = request.GET.get('search', '')
    status = request.GET.get('status', 'active')
    
    # Query base
    schedules = WorkSchedule.objects.select_related('shift_template', 'created_by')
    
    # Aplicar filtros
    if status == 'active':
        schedules = schedules.filter(is_active=True)
    elif status == 'inactive':
        schedules = schedules.filter(is_active=False)
    
    if schedule_type:
        schedules = schedules.filter(schedule_type=schedule_type)
    if template_id:
        schedules = schedules.filter(shift_template_id=template_id)
    if search:
        schedules = schedules.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search)
        )
    
    # Ordenar
    schedules = schedules.order_by('-created_at')
    
    # Paginación
    paginator = Paginator(schedules, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Opciones para filtros
    templates = ShiftTemplate.objects.filter(is_active=True).order_by('name')
    schedule_types = WorkSchedule.SCHEDULE_TYPES
    
    context = {
        'page_obj': page_obj,
        'schedules': page_obj.object_list,
        'templates': templates,
        'schedule_types': schedule_types,
        'current_schedule_type': schedule_type,
        'current_template': template_id,
        'current_search': search,
        'current_status': status,
        'show_assignment': show_assignment,
        'page_title': 'Centro de Asignación de Empleados' if show_assignment else 'Horarios de Trabajo',
        'breadcrumb': [
            {'name': 'Inicio', 'url': '/'},
            {'name': 'Asistencia', 'url': '/asistencia/'},
            {'name': 'Gestión de Turnos', 'url': '/asistencia/turnos/'},
            {'name': 'Horarios', 'url': ''}
        ]
    }
    
    return render(request, 'attendance/shifts/schedules_list.html', context)


@csrf_exempt
@login_required
@permission_required('supervisor')
def assign_employee_to_shift(request):
    """
    API para asignar empleados a turnos
    """
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        employee_id = data.get('employee_id')
        shift_id = data.get('shift_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Validaciones
        employee = get_object_or_404(Employee, id=employee_id, is_active=True)
        shift = get_object_or_404(Shift, id=shift_id, is_active=True)
        
        # Crear asignación
        assignment = EmployeeShiftAssignment.objects.create(
            employee=employee,
            shift=shift,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
            assigned_by=request.user,
            notes=data.get('notes', '')
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Empleado {employee.get_full_name()} asignado al turno {shift} exitosamente',
            'assignment_id': assignment.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@login_required
@permission_required('supervisor')
def get_available_employees(request):
    """
    API para obtener empleados disponibles para asignación
    """
    try:
        # Obtener empleados activos
        employees = Employee.objects.filter(is_active=True).select_related('department', 'position')
        
        # Filtros opcionales
        department_id = request.GET.get('department')
        position_id = request.GET.get('position')
        search = request.GET.get('search')
        
        if department_id:
            employees = employees.filter(department_id=department_id)
        
        if position_id:
            employees = employees.filter(position_id=position_id)
        
        if search:
            employees = employees.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        # Serializar datos
        employees_data = []
        for emp in employees[:50]:  # Limitar a 50 resultados
            employees_data.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'full_name': emp.get_full_name(),
                'department': emp.department.name if emp.department else 'Sin departamento',
                'position': emp.position.title if emp.position else 'Sin puesto',
                'photo_url': None,  # Campo photo no existe en Employee
                'current_assignments': emp.shift_assignments.filter(status='ACTIVE').count()
            })
        
        return JsonResponse({
            'success': True,
            'employees': employees_data,
            'total': employees.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@login_required
@permission_required('supervisor')
def bulk_assign_employees(request):
    """
    API para asignación masiva de empleados a turnos
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        employee_ids = data.get('employee_ids', [])
        shift_id = data.get('shift_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        notes = data.get('notes', '')
        
        if not employee_ids or not shift_id or not start_date:
            return JsonResponse({
                'success': False,
                'error': 'Faltan datos requeridos'
            }, status=400)
        
        # Validar turno
        shift = get_object_or_404(Shift, id=shift_id, is_active=True)
        
        # Procesar asignaciones
        assignments_created = []
        errors = []
        
        for emp_id in employee_ids:
            try:
                employee = Employee.objects.get(id=emp_id, is_active=True)
                
                # Verificar si ya tiene asignación activa para este turno
                existing = EmployeeShiftAssignment.objects.filter(
                    employee=employee,
                    shift=shift,
                    status='ACTIVE',
                    start_date__lte=start_date
                ).filter(
                    Q(end_date__isnull=True) | Q(end_date__gte=start_date)
                ).exists()
                
                if existing:
                    errors.append(f'{employee.get_full_name()} ya tiene una asignación activa para este turno')
                    continue
                
                # Crear asignación
                assignment = EmployeeShiftAssignment.objects.create(
                    employee=employee,
                    shift=shift,
                    start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
                    end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
                    assigned_by=request.user,
                    notes=notes
                )
                
                assignments_created.append({
                    'employee_name': employee.get_full_name(),
                    'assignment_id': assignment.id
                })
                
            except Employee.DoesNotExist:
                errors.append(f'Empleado con ID {emp_id} no encontrado')
            except Exception as e:
                errors.append(f'Error asignando empleado ID {emp_id}: {str(e)}')
        
        return JsonResponse({
            'success': True,
            'assignments_created': len(assignments_created),
            'assignments': assignments_created,
            'errors': errors,
            'message': f'Se crearon {len(assignments_created)} asignaciones exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@permission_required('supervisor')
def edit_shift_template(request, template_id):
    """Editar una plantilla de turno existente"""
    template = get_object_or_404(ShiftTemplate, id=template_id)
    
    if request.method == 'POST':
        try:
            template.name = request.POST.get('name')
            template.description = request.POST.get('description', '')
            template.category = request.POST.get('category')
            template.shift_type = request.POST.get('shift_type')
            template.start_time = request.POST.get('start_time')
            template.end_time = request.POST.get('end_time')
            template.monday = 'monday' in request.POST
            template.tuesday = 'tuesday' in request.POST
            template.wednesday = 'wednesday' in request.POST
            template.thursday = 'thursday' in request.POST
            template.friday = 'friday' in request.POST
            template.saturday = 'saturday' in request.POST
            template.sunday = 'sunday' in request.POST
            template.break_duration = request.POST.get('break_duration', 0)
            template.is_overnight = 'is_overnight' in request.POST
            template.color = request.POST.get('color', '#007bff')
            template.save()
            
            # Actualizar todos los turnos asociados a horarios que usan esta plantilla
            work_schedules = WorkSchedule.objects.filter(shift_template=template, is_active=True)
            shifts_updated = 0
            for schedule in work_schedules:
                shifts = schedule.shifts.all()
                for shift in shifts:
                    shift.start_time = template.start_time
                    shift.end_time = template.end_time
                    shift.is_overnight = template.is_overnight
                    shift.save()
                    shifts_updated += 1
            
            if shifts_updated > 0:
                messages.success(request, f'Plantilla "{template.name}" y {shifts_updated} turno(s) en {work_schedules.count()} horario(s) actualizados exitosamente.')
            else:
                messages.success(request, f'Plantilla "{template.name}" actualizada exitosamente.')
            return redirect('attendance:shift_template_detail', template_id=template.id)
        except Exception as e:
            messages.error(request, f'Error al actualizar la plantilla: {str(e)}')
    
    context = {
        'template': template,
        'categories': ShiftTemplate.TEMPLATE_CATEGORIES,
        'shift_types': ShiftTemplate.SHIFT_TYPES,
        'page_title': f'Editar Plantilla: {template.name}',
    }
    return render(request, 'attendance/shifts/template_edit.html', context)


@login_required
@permission_required('supervisor')
def delete_shift_template(request, template_id):
    """Eliminar (desactivar) una plantilla de turno"""
    template = get_object_or_404(ShiftTemplate, id=template_id)
    
    if request.method == 'POST':
        try:
            schedules_count = WorkSchedule.objects.filter(template=template, is_active=True).count()
            if schedules_count > 0:
                messages.warning(request, f'No se puede eliminar la plantilla "{template.name}" porque está siendo utilizada en {schedules_count} horario(s) activo(s).')
                return redirect('attendance:shift_template_detail', template_id=template.id)
            
            template.is_active = False
            template.save()
            messages.success(request, f'Plantilla "{template.name}" eliminada exitosamente.')
            return redirect('attendance:shift_templates_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar la plantilla: {str(e)}')
            return redirect('attendance:shift_template_detail', template_id=template.id)
    
    context = {
        'template': template,
        'schedules_count': WorkSchedule.objects.filter(template=template, is_active=True).count(),
        'page_title': f'Eliminar Plantilla: {template.name}',
    }
    return render(request, 'attendance/shifts/template_delete_confirm.html', context)
