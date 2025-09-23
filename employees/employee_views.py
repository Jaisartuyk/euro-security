"""
Vistas específicas para empleados (self-service)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Employee
from core.permissions import employee_required, get_employee_from_user, permission_required
from django.db.models import Count, Q
from datetime import datetime, timedelta


@employee_required
def employee_profile(request):
    """Vista para que el empleado vea su propio perfil"""
    employee = get_employee_from_user(request.user)
    
    context = {
        'employee': employee,
        'is_own_profile': True,
    }
    
    return render(request, 'employees/employee_profile.html', context)


@employee_required
def employee_dashboard(request):
    """Dashboard personalizado para empleados según su nivel"""
    employee = get_employee_from_user(request.user)
    permission_level = employee.get_permission_level()
    
    # Determinar el tipo de dashboard según el puesto
    dashboard_type = get_dashboard_type(employee)
    
    # Datos específicos según el tipo de empleado
    context = {
        'employee': employee,
        'permission_level': permission_level,
        'dashboard_type': dashboard_type,
        'can_view_all_employees': employee.can_view_all_employees(),
        'can_edit_employees': employee.can_edit_employees(),
        'can_view_reports': employee.can_view_reports(),
        'can_view_payroll': employee.can_view_payroll(),
    }
    
    # Agregar datos específicos según el tipo de dashboard
    if dashboard_type == 'security_guard':
        context.update(get_security_guard_data(employee))
    elif dashboard_type == 'supervisor':
        context.update(get_supervisor_data(employee))
    elif dashboard_type == 'manager':
        context.update(get_manager_data(employee))
    elif dashboard_type == 'director':
        context.update(get_director_data(employee))
    
    # Seleccionar plantilla específica
    template_name = f'employees/dashboards/{dashboard_type}_dashboard.html'
    
    return render(request, template_name, context)


@permission_required('supervisor')
def employee_team(request):
    """Vista para que supervisores vean su equipo"""
    employee = get_employee_from_user(request.user)
    
    # Solo supervisores y superiores pueden ver equipos
    if employee.get_permission_level() not in ['supervisor', 'management', 'full']:
        messages.error(request, 'No tienes permisos para ver información de equipo.')
        return redirect('employee_dashboard')
    
    # Obtener empleados del mismo departamento
    team_members = Employee.objects.filter(
        department=employee.department,
        is_active=True
    ).exclude(pk=employee.pk).select_related('position', 'user')
    
    context = {
        'employee': employee,
        'team_members': team_members,
        'department': employee.department,
    }
    
    return render(request, 'employees/employee_team.html', context)


@employee_required
def employee_change_password(request):
    """Vista para que el empleado cambie su contraseña"""
    employee = get_employee_from_user(request.user)
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validaciones
        if not request.user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta.')
        elif new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
        elif len(new_password) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
        else:
            # Cambiar contraseña
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('employee_profile')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'employees/change_password.html', context)


@employee_required
def employee_permissions_info(request):
    """Vista para mostrar información sobre permisos del empleado"""
    employee = get_employee_from_user(request.user)
    
    permission_descriptions = {
        'basic': {
            'level': 'Básico',
            'description': 'Acceso a tu perfil personal únicamente',
            'permissions': [
                'Ver tu información personal',
                'Cambiar tu contraseña',
                'Ver tu información de contacto'
            ]
        },
        'standard': {
            'level': 'Estándar',
            'description': 'Acceso básico con algunas funciones adicionales',
            'permissions': [
                'Ver tu información personal',
                'Cambiar tu contraseña',
                'Ver información básica del departamento'
            ]
        },
        'advanced': {
            'level': 'Avanzado',
            'description': 'Acceso a funciones avanzadas',
            'permissions': [
                'Ver tu información personal',
                'Cambiar tu contraseña',
                'Ver información del departamento',
                'Acceso a algunos reportes'
            ]
        },
        'supervisor': {
            'level': 'Supervisor',
            'description': 'Gestión de equipo y reportes',
            'permissions': [
                'Ver información de tu equipo',
                'Acceso a reportes departamentales',
                'Ver empleados del departamento',
                'Gestionar información del equipo'
            ]
        },
        'management': {
            'level': 'Gerencial',
            'description': 'Gestión completa de empleados y reportes',
            'permissions': [
                'Ver todos los empleados',
                'Editar información de empleados',
                'Acceso completo a reportes',
                'Ver información de nómina',
                'Gestionar departamento'
            ]
        },
        'full': {
            'level': 'Directivo',
            'description': 'Acceso completo al sistema',
            'permissions': [
                'Acceso completo a todos los módulos',
                'Gestión completa de empleados',
                'Acceso a toda la información financiera',
                'Configuración del sistema',
                'Gestión de usuarios y permisos'
            ]
        }
    }
    
    permission_level = employee.get_permission_level()
    permission_info = permission_descriptions.get(permission_level, permission_descriptions['basic'])
    
    return JsonResponse({
        'employee': {
            'name': employee.get_full_name(),
            'position': employee.position.title if employee.position else 'Sin puesto',
            'department': employee.department.name if employee.department else 'Sin departamento',
        },
        'permission_level': permission_level,
        'permission_info': permission_info,
        'capabilities': {
            'can_view_all_employees': employee.can_view_all_employees(),
            'can_edit_employees': employee.can_edit_employees(),
            'can_view_reports': employee.can_view_reports(),
            'can_view_payroll': employee.can_view_payroll(),
        }
    })


# ============================================================================
# FUNCIONES AUXILIARES PARA DASHBOARDS ESPECÍFICOS
# ============================================================================

def get_dashboard_type(employee):
    """Determina el tipo de dashboard según el puesto del empleado"""
    position_code = employee.position.code
    department_code = employee.department.code
    level = employee.position.level
    
    # Guardias de seguridad (departamento OPS-SEC)
    if department_code == 'OPS-SEC':
        if level in ['ENTRY', 'JUNIOR']:
            return 'security_guard'
        elif level == 'SENIOR':
            return 'senior_guard'
        elif level == 'LEAD':
            return 'supervisor'
        elif level == 'MANAGER':
            return 'manager'
        elif level == 'DIRECTOR':
            return 'director'
    
    # Otros departamentos
    if level == 'DIRECTOR':
        return 'director'
    elif level == 'MANAGER':
        return 'manager'
    elif level == 'LEAD':
        return 'supervisor'
    elif level in ['SENIOR', 'JUNIOR']:
        return 'employee'
    else:
        return 'employee'


def get_security_guard_data(employee):
    """Datos específicos para guardias de seguridad básicos"""
    from .models import Employee
    
    # Información de turno y zona
    position_info = {
        'GUA-I': {'zone': 'Acceso Principal', 'shift': 'Rotativo'},
        'GUA-ACC': {'zone': 'Control de Acceso', 'shift': 'Diurno'},
        'VIG-NOC': {'zone': 'Vigilancia General', 'shift': 'Nocturno'},
        'GUA-II': {'zone': 'Patrullaje', 'shift': 'Rotativo'},
        'GUA-PAT': {'zone': 'Patrullaje Móvil', 'shift': 'Diurno'},
        'OP-CCTV': {'zone': 'Centro de Monitoreo', 'shift': 'Rotativo'},
    }
    
    # Supervisor directo
    supervisor = Employee.objects.filter(
        department=employee.department,
        position__level='LEAD'
    ).first()
    
    # Compañeros de turno
    teammates = Employee.objects.filter(
        department=employee.department,
        position__level__in=['ENTRY', 'JUNIOR'],
        is_active=True
    ).exclude(id=employee.id)[:5]
    
    # Información de contactos de emergencia
    emergency_contacts = {
        'supervisor': supervisor,
        'central': '555-0911',
        'emergencia': '911',
        'soporte_tecnico': '555-0500'
    }
    
    return {
        'zone_info': position_info.get(employee.position.code, {'zone': 'Asignada', 'shift': 'Rotativo'}),
        'supervisor': supervisor,
        'teammates': teammates,
        'emergency_contacts': emergency_contacts,
        'recent_alerts': get_recent_alerts(),
        'shift_schedule': get_shift_schedule(employee),
    }


def get_supervisor_data(employee):
    """Datos específicos para supervisores"""
    from .models import Employee
    
    # Equipo a cargo
    team_members = Employee.objects.filter(
        department=employee.department,
        position__level__in=['ENTRY', 'JUNIOR', 'SENIOR'],
        is_active=True
    )
    
    # Estadísticas del equipo
    team_stats = {
        'total_guards': team_members.count(),
        'active_today': team_members.count(),
        'on_patrol': team_members.filter(position__code__contains='PAT').count(),
        'on_cctv': team_members.filter(position__code__contains='CCTV').count(),
    }
    
    return {
        'team_members': team_members,
        'team_stats': team_stats,
        'recent_incidents': get_recent_incidents(employee.department),
        'zones_coverage': get_zones_coverage(),
        'shift_assignments': get_shift_assignments(employee),
    }


def get_manager_data(employee):
    """Datos específicos para gerentes"""
    from .models import Employee
    
    # Todo el departamento
    department_staff = Employee.objects.filter(
        department=employee.department,
        is_active=True
    )
    
    # Estadísticas departamentales
    dept_stats = {
        'total_staff': department_staff.count(),
        'supervisors': department_staff.filter(position__level='LEAD').count(),
        'senior_guards': department_staff.filter(position__level='SENIOR').count(),
        'regular_guards': department_staff.filter(position__level__in=['JUNIOR', 'ENTRY']).count(),
    }
    
    return {
        'department_staff': department_staff,
        'dept_stats': dept_stats,
        'monthly_reports': get_monthly_reports(),
        'budget_info': get_budget_info(employee.department),
        'performance_metrics': get_performance_metrics(),
    }


def get_director_data(employee):
    """Datos específicos para directores"""
    from .models import Employee
    
    # Toda la empresa
    all_staff = Employee.objects.filter(is_active=True)
    
    # Estadísticas globales
    global_stats = {
        'total_employees': all_staff.count(),
        'by_department': all_staff.values('department__name').annotate(count=Count('id')),
        'by_level': all_staff.values('position__level').annotate(count=Count('id')),
    }
    
    return {
        'all_staff': all_staff,
        'global_stats': global_stats,
        'executive_reports': get_executive_reports(),
        'financial_summary': get_financial_summary(),
        'strategic_metrics': get_strategic_metrics(),
    }


# Funciones de datos simulados
def get_recent_alerts():
    return [
        {'time': '14:30', 'type': 'info', 'message': 'Cambio de turno en 30 minutos'},
        {'time': '13:15', 'type': 'warning', 'message': 'Revisar sector B - cámara offline'},
        {'time': '12:00', 'type': 'success', 'message': 'Ronda completada exitosamente'},
    ]

def get_shift_schedule(employee):
    return {
        'current_shift': '06:00 - 14:00',
        'next_shift': '14:00 - 22:00',
        'days_off': ['Domingo'],
        'overtime_hours': 8,
    }

def get_recent_incidents(department):
    return [
        {'time': '15:45', 'zone': 'Acceso Principal', 'type': 'Menor', 'status': 'Resuelto'},
        {'time': '14:20', 'zone': 'Estacionamiento', 'type': 'Rutina', 'status': 'En proceso'},
        {'time': '13:10', 'zone': 'Perímetro Norte', 'type': 'Preventivo', 'status': 'Cerrado'},
    ]

def get_zones_coverage():
    return {
        'total_zones': 12,
        'covered': 11,
        'uncovered': 1,
        'zones': [
            {'name': 'Acceso Principal', 'status': 'Cubierto', 'guard': 'Luis García'},
            {'name': 'Estacionamiento', 'status': 'Cubierto', 'guard': 'María Fernández'},
            {'name': 'Perímetro Norte', 'status': 'Descubierto', 'guard': None},
        ]
    }

def get_shift_assignments(employee):
    return {
        'morning': ['Luis García', 'María Fernández'],
        'afternoon': ['Carlos Herrera', 'Isabel Vega'],
        'night': ['Andrés Mendoza', 'Patricia Ramírez'],
    }

def get_monthly_reports():
    return {
        'incidents': 45,
        'resolved': 42,
        'pending': 3,
        'efficiency': 93.3,
    }

def get_budget_info(department):
    return {
        'allocated': 500000,
        'spent': 387500,
        'remaining': 112500,
        'percentage_used': 77.5,
    }

def get_performance_metrics():
    return {
        'response_time': '3.2 min',
        'coverage': '91.7%',
        'satisfaction': '4.6/5',
        'incidents_prevented': 23,
    }

def get_executive_reports():
    return {
        'monthly_revenue': 2500000,
        'client_retention': 94.2,
        'new_contracts': 8,
        'employee_satisfaction': 4.3,
    }

def get_financial_summary():
    return {
        'total_revenue': 2500000,
        'total_expenses': 1875000,
        'profit_margin': 25.0,
        'growth_rate': 12.5,
    }

def get_strategic_metrics():
    return {
        'market_share': 15.8,
        'client_satisfaction': 4.7,
        'employee_turnover': 8.2,
        'operational_efficiency': 89.3,
    }
