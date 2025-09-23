"""
Context processors para EURO SECURITY
Hace disponible información global en todos los templates
"""
from employees.models import Employee

def attendance_permissions(request):
    """
    Agrega información de permisos de asistencia al contexto
    """
    context = {
        'can_view_attendance_dashboard': False,
        'can_view_attendance_reports': False,
        'can_view_location_maps': False,
        'can_export_reports': False,
        'attendance_permission_level': 'none',
        'has_employee_profile': False,
    }
    
    if request.user.is_authenticated:
        # SUPERUSUARIOS: Acceso completo automático
        if request.user.is_superuser:
            context['has_employee_profile'] = True  # Simular que tiene perfil
            context['can_view_attendance_dashboard'] = True
            context['can_view_attendance_reports'] = True
            context['can_view_location_maps'] = True
            context['can_export_reports'] = True
            context['attendance_permission_level'] = 'superuser'
            return context
        
        # STAFF: Acceso de administrador
        if request.user.is_staff:
            context['has_employee_profile'] = True
            context['can_view_attendance_dashboard'] = True
            context['can_view_attendance_reports'] = True
            context['can_view_location_maps'] = True
            context['can_export_reports'] = True
            context['attendance_permission_level'] = 'staff'
            return context
        
        # EMPLEADOS REGULARES: Verificar perfil
        try:
            # Verificar si el usuario tiene perfil de empleado
            employee = Employee.objects.get(user=request.user)
            context['has_employee_profile'] = True
            
            # Importar aquí para evitar imports circulares
            from attendance.permissions import AttendancePermissions
            
            # Obtener nivel de permisos
            permission_level = AttendancePermissions.get_permission_level(request.user)
            context['attendance_permission_level'] = permission_level
            
            # Determinar permisos específicos
            if permission_level in ['full', 'management', 'supervisor']:
                context['can_view_attendance_dashboard'] = True
                context['can_view_attendance_reports'] = True
            
            if permission_level in ['full', 'management']:
                context['can_view_location_maps'] = True
                context['can_export_reports'] = True
            
            # Supervisores también pueden ver mapas
            if permission_level == 'supervisor':
                context['can_view_location_maps'] = True
                
        except Employee.DoesNotExist:
            # Usuario autenticado pero sin perfil de empleado
            context['has_employee_profile'] = False
    
    return context

def company_info(request):
    """
    Información de la empresa disponible en todos los templates
    """
    return {
        'company_name': 'EURO SECURITY',
        'company_tagline': 'Seguridad Física Profesional',
        'company_version': '2.0',
    }
