"""
Vistas para reportes de asistencia y mapas
EURO SECURITY - Attendance Reports & Maps
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.db.models import Count, Avg, Q
from django.utils import timezone
from django.conf import settings
from datetime import datetime, date, timedelta
import json

from core.permissions import employee_required
from .models import AttendanceRecord, AttendanceSummary
from .permissions import AttendancePermissions, attendance_permission_required
from employees.models import Employee
from departments.models import Department
from .models import EmployeeShiftAssignment, WorkSchedule, Shift
import calendar

@login_required
@employee_required
def attendance_reports(request):
    """Vista principal de reportes de asistencia"""
    user_permissions = AttendancePermissions.get_permission_level(request.user)
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    viewable_departments = AttendancePermissions.get_viewable_departments(request.user)
    
    # Filtros de fecha
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Estadísticas generales
    total_employees = viewable_employees.count()
    present_today = AttendanceSummary.objects.filter(
        employee__in=viewable_employees,
        date=today,
        is_present=True
    ).count()
    
    late_today = AttendanceSummary.objects.filter(
        employee__in=viewable_employees,
        date=today,
        is_late=True
    ).count()
    
    # Reportes por departamento
    department_stats = []
    for dept in viewable_departments:
        dept_employees = viewable_employees.filter(department=dept)
        dept_present = AttendanceSummary.objects.filter(
            employee__in=dept_employees,
            date=today,
            is_present=True
        ).count()
        
        department_stats.append({
            'department': dept,
            'total_employees': dept_employees.count(),
            'present_today': dept_present,
            'attendance_rate': (dept_present / dept_employees.count() * 100) if dept_employees.count() > 0 else 0
        })
    
    context = {
        'user_permissions': user_permissions,
        'permission_description': AttendancePermissions.get_permission_description(request.user),
        'can_view_maps': AttendancePermissions.can_view_location_maps(request.user),
        'can_export': AttendancePermissions.can_export_reports(request.user),
        'total_employees': total_employees,
        'present_today': present_today,
        'late_today': late_today,
        'department_stats': department_stats,
        'start_date': start_date,
        'end_date': end_date,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    
    return render(request, 'attendance/reports.html', context)

@login_required
@employee_required
@attendance_permission_required('supervisor')
def department_attendance_report(request, department_id):
    """Reporte detallado de asistencia por departamento"""
    department = get_object_or_404(Department, id=department_id)
    
    # SUPERUSUARIOS: Acceso automático sin restricciones
    if not (request.user.is_superuser or request.user.is_staff):
        viewable_departments = AttendancePermissions.get_viewable_departments(request.user)
        if department not in viewable_departments:
            return HttpResponseForbidden("No tienes permisos para ver este departamento")
    
    # Filtros de fecha
    today = timezone.now().date()
    start_date = request.GET.get('start_date', today.replace(day=1))
    end_date = request.GET.get('end_date', today)
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Empleados del departamento
    employees = Employee.objects.filter(department=department)
    
    # Resúmenes de asistencia
    summaries = AttendanceSummary.objects.filter(
        employee__in=employees,
        date__range=[start_date, end_date]
    ).select_related('employee').order_by('-date', 'employee__first_name')
    
    # Estadísticas del departamento
    total_days = (end_date - start_date).days + 1
    total_possible_attendances = employees.count() * total_days
    total_present = summaries.filter(is_present=True).count()
    total_late = summaries.filter(is_late=True).count()
    
    context = {
        'department': department,
        'employees': employees,
        'summaries': summaries,
        'start_date': start_date,
        'end_date': end_date,
        'total_employees': employees.count(),
        'total_days': total_days,
        'total_present': total_present,
        'total_late': total_late,
        'attendance_rate': (total_present / total_possible_attendances * 100) if total_possible_attendances > 0 else 0,
        'punctuality_rate': ((total_present - total_late) / total_present * 100) if total_present > 0 else 0,
    }
    
    return render(request, 'attendance/department_report.html', context)

@login_required
def attendance_locations_map(request):
    """Vista del mapa de ubicaciones de asistencia"""
    # SUPERUSUARIOS: Acceso automático sin restricciones
    if not (request.user.is_superuser or request.user.is_staff):
        if not AttendancePermissions.can_view_location_maps(request.user):
            return HttpResponseForbidden("No tienes permisos para ver mapas de ubicación")
    
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    
    # Filtros de fecha - manejar zona horaria UTC
    today = timezone.now().date()
    date_filter = request.GET.get('date', today)
    
    if isinstance(date_filter, str):
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
    
    # Convertir fecha a rango UTC para buscar correctamente
    start_datetime = timezone.make_aware(datetime.combine(date_filter, datetime.min.time()))
    end_datetime = start_datetime + timedelta(days=1)
    
    # Registros GPS del día seleccionado
    from .models_gps import GPSTracking
    
    # Debug logging
    print(f"🔍 MAPA DEBUG - Usuario: {request.user.username}")
    print(f"🔍 MAPA DEBUG - Es superusuario: {request.user.is_superuser}")
    print(f"🔍 MAPA DEBUG - Fecha filtro: {date_filter}")
    
    # Contar todos los registros GPS sin filtro de fecha
    total_gps_records = GPSTracking.objects.count()
    print(f"🔍 MAPA DEBUG - Total registros GPS en BD: {total_gps_records}")
    
    # Contar registros GPS de hoy
    today_records = GPSTracking.objects.filter(timestamp__date=timezone.now().date()).count()
    print(f"🔍 MAPA DEBUG - Registros GPS de hoy: {today_records}")
    
    # Filtrar por empleados visibles (incluyendo registros sin empleado para superusuarios)
    if request.user.is_superuser or request.user.is_staff:
        # Superusuarios ven todos los registros GPS usando rango UTC
        records_with_location = GPSTracking.objects.filter(
            timestamp__gte=start_datetime,
            timestamp__lt=end_datetime
        ).select_related('employee').order_by('-timestamp')
        print(f"🔍 MAPA DEBUG - Registros encontrados (superusuario): {records_with_location.count()}")
        print(f"🔍 MAPA DEBUG - Rango UTC: {start_datetime} a {end_datetime}")
    else:
        # Usuarios normales solo ven GPS de empleados que pueden ver
        viewable_count = viewable_employees.count()
        print(f"🔍 MAPA DEBUG - Empleados visibles: {viewable_count}")
        
        records_with_location = GPSTracking.objects.filter(
            employee__in=viewable_employees,
            timestamp__gte=start_datetime,
            timestamp__lt=end_datetime
        ).select_related('employee').order_by('-timestamp')
        print(f"🔍 MAPA DEBUG - Registros encontrados (usuario normal): {records_with_location.count()}")
    
    context = {
        'records': records_with_location,
        'selected_date': date_filter,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'total_locations': records_with_location.count(),
    }
    
    return render(request, 'attendance/locations_map.html', context)

@login_required
@employee_required
def attendance_locations_api(request):
    """API para obtener ubicaciones de asistencia en formato JSON"""
    if not AttendancePermissions.can_view_location_maps(request.user):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    
    # Filtros
    date_filter = request.GET.get('date', timezone.now().date())
    if isinstance(date_filter, str):
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
    
    # Obtener registros con ubicación
    records = AttendanceRecord.objects.filter(
        employee__in=viewable_employees,
        timestamp__date=date_filter,
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('employee')
    
    # Formatear para el mapa
    locations = []
    for record in records:
        locations.append({
            'id': record.id,
            'employee_name': record.employee.get_full_name(),
            'employee_id': record.employee.id,
            'department': record.employee.department.name if record.employee.department else 'Sin departamento',
            'attendance_type': record.get_attendance_type_display(),
            'timestamp': record.timestamp.strftime('%H:%M:%S'),
            'latitude': float(record.latitude),
            'longitude': float(record.longitude),
            'accuracy': record.location_accuracy,
            'address': record.address,
            'confidence': record.facial_confidence,
            'verification_method': record.get_verification_method_display(),
        })
    
    return JsonResponse({
        'locations': locations,
        'total': len(locations),
        'date': date_filter.isoformat()
    })

@login_required
@employee_required
@attendance_permission_required('management')
def export_attendance_report(request):
    """Exportar reporte de asistencias (solo para MANAGER y DIRECTOR)"""
    import csv
    from django.http import HttpResponse
    
    viewable_employees = AttendancePermissions.get_viewable_employees(request.user)
    
    # Filtros
    start_date = request.GET.get('start_date', timezone.now().date().replace(day=1))
    end_date = request.GET.get('end_date', timezone.now().date())
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="asistencias_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Empleado', 'Departamento', 'Fecha', 'Primera Entrada', 'Última Salida',
        'Horas Trabajadas', 'Presente', 'Tarde', 'Salida Temprana'
    ])
    
    summaries = AttendanceSummary.objects.filter(
        employee__in=viewable_employees,
        date__range=[start_date, end_date]
    ).select_related('employee', 'employee__department').order_by('employee__first_name', 'date')
    
    for summary in summaries:
        writer.writerow([
            summary.employee.get_full_name(),
            summary.employee.department.name if summary.employee.department else 'Sin departamento',
            summary.date.strftime('%Y-%m-%d'),
            summary.first_entry.strftime('%H:%M:%S') if summary.first_entry else '',
            summary.last_exit.strftime('%H:%M:%S') if summary.last_exit else '',
            summary.get_work_hours_display(),
            'Sí' if summary.is_present else 'No',
            'Sí' if summary.is_late else 'No',
            'Sí' if summary.is_early_exit else 'No',
        ])
    
    return response


@login_required
@employee_required
@attendance_permission_required('supervisor')
def monthly_payroll_report(request, department_id):
    """
    Reporte mensual tipo nómina con calendario y códigos de turno coloreados
    Formato: Empleados en filas, días del mes en columnas
    """
    department = get_object_or_404(Department, id=department_id)
    
    # Verificar permisos
    if not (request.user.is_superuser or request.user.is_staff):
        viewable_departments = AttendancePermissions.get_viewable_departments(request.user)
        if department not in viewable_departments:
            return HttpResponseForbidden("No tienes permisos para ver este departamento")
    
    # Obtener mes y año de los parámetros o usar actual
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    
    # Calcular primer y último día del mes
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Obtener empleados del departamento activos
    employees = Employee.objects.filter(
        department=department,
        is_active=True
    ).order_by('first_name', 'last_name')
    
    # Nombres de meses en español
    month_names = [
        '', 'ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
        'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE'
    ]
    
    # Generar lista de días del mes
    days_in_month = calendar.monthrange(year, month)[1]
    days_list = list(range(1, days_in_month + 1))
    
    # Construir datos para cada empleado
    employees_data = []
    
    for employee in employees:
        employee_info = {
            'employee': employee,
            'days': []
        }
        
        # Para cada día del mes
        for day in days_list:
            current_date = date(year, month, day)
            
            # Buscar asignación de turno para ese día
            assignment = EmployeeShiftAssignment.objects.filter(
                employee=employee,
                start_date__lte=current_date,
                status='ACTIVE'
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=current_date)
            ).select_related('shift', 'shift__work_schedule__shift_template').first()
            
            # Buscar registro de asistencia
            attendance = AttendanceSummary.objects.filter(
                employee=employee,
                date=current_date
            ).first()
            
            day_info = {
                'day': day,
                'date': current_date,
                'shift_code': None,
                'shift_color': '#f3f4f6',  # Gris por defecto
                'shift_name': '',
                'present': False,
                'late': False,
                'absent': False,
            }
            
            if assignment and assignment.shift:
                # Obtener template del turno
                template = assignment.shift.work_schedule.shift_template
                
                # Usar código de turno si existe
                if hasattr(template, 'shift_code') and template.shift_code:
                    day_info['shift_code'] = template.shift_code
                else:
                    # Usar primera letra del nombre del turno
                    day_info['shift_code'] = assignment.shift.name[:1].upper()
                
                # Obtener color del turno
                if hasattr(template, 'color') and template.color:
                    day_info['shift_color'] = template.color
                elif assignment.shift.color:
                    day_info['shift_color'] = assignment.shift.color
                
                day_info['shift_name'] = template.name
            
            # Información de asistencia
            if attendance:
                day_info['present'] = attendance.is_present
                day_info['late'] = attendance.is_late
                day_info['absent'] = not attendance.is_present
            elif assignment and current_date < today:
                # Si hay turno asignado pero no hay registro y ya pasó la fecha
                day_info['absent'] = True
            
            employee_info['days'].append(day_info)
        
        # Calcular estadísticas del empleado
        employee_info['stats'] = {
            'total_days': len([d for d in employee_info['days'] if d['shift_code']]),
            'days_present': len([d for d in employee_info['days'] if d['present']]),
            'days_late': len([d for d in employee_info['days'] if d['late']]),
            'days_absent': len([d for d in employee_info['days'] if d['absent']]),
        }
        
        employees_data.append(employee_info)
    
    context = {
        'department': department,
        'month': month,
        'year': year,
        'month_name': month_names[month],
        'days_list': days_list,
        'employees_data': employees_data,
        'first_day': first_day,
        'last_day': last_day,
        'page_title': f'Nómina Mensual - {department.name} - {month_names[month]} {year}',
    }
    
    return render(request, 'attendance/monthly_payroll_report.html', context)
