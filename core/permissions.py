"""
Sistema de permisos personalizado para EURO SECURITY
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import Http404
from employees.models import Employee


def get_employee_from_user(user):
    """Obtiene el empleado asociado al usuario"""
    try:
        return Employee.objects.select_related('position', 'department').get(user=user)
    except Employee.DoesNotExist:
        return None


def employee_required(view_func):
    """Decorador que requiere que el usuario tenga un perfil de empleado"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login')
        
        # SUPERUSUARIOS: Acceso automático sin restricciones
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)
        
        employee = get_employee_from_user(request.user)
        if not employee:
            messages.error(request, 'No se encontró tu perfil de empleado. Contacta al administrador.')
            return redirect('dashboard:home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def permission_required(permission_level):
    """
    Decorador para requerir un nivel de permisos específico
    
    Niveles de permisos:
    - 'basic': Empleados básicos
    - 'standard': Empleados junior
    - 'advanced': Empleados senior
    - 'supervisor': Supervisores/Lead
    - 'management': Gerentes
    - 'full': Directores
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Los superusuarios tienen acceso completo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            employee = get_employee_from_user(request.user)
            if not employee:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('dashboard:home')
            
            user_permission = employee.get_permission_level()
            
            # Mapear niveles a números para comparación
            permission_hierarchy = {
                'basic': 1,
                'standard': 2,
                'advanced': 3,
                'supervisor': 4,
                'management': 5,
                'full': 6
            }
            
            required_level = permission_hierarchy.get(permission_level, 1)
            user_level = permission_hierarchy.get(user_permission, 1)
            
            if user_level < required_level:
                messages.error(request, 'No tienes permisos suficientes para acceder a esta sección.')
                return redirect('dashboard:home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def can_view_employee_data(user, target_employee=None):
    """
    Determina si un usuario puede ver datos de empleados
    
    Args:
        user: Usuario que solicita acceso
        target_employee: Empleado objetivo (opcional)
    
    Returns:
        bool: True si puede ver los datos
    """
    if user.is_superuser:
        return True
    
    employee = get_employee_from_user(user)
    if not employee:
        return False
    
    # Si no se especifica empleado objetivo, verificar permisos generales
    if not target_employee:
        return employee.can_view_all_employees()
    
    # Los empleados siempre pueden ver sus propios datos
    if employee == target_employee:
        return True
    
    # Verificar si puede ver todos los empleados
    if employee.can_view_all_employees():
        return True
    
    # Los supervisores pueden ver empleados de su departamento
    if (employee.get_permission_level() in ['supervisor', 'management', 'full'] and 
        employee.department == target_employee.department):
        return True
    
    return False


def can_edit_employee_data(user, target_employee=None):
    """
    Determina si un usuario puede editar datos de empleados
    
    Args:
        user: Usuario que solicita acceso
        target_employee: Empleado objetivo (opcional)
    
    Returns:
        bool: True si puede editar los datos
    """
    if user.is_superuser:
        return True
    
    employee = get_employee_from_user(user)
    if not employee:
        return False
    
    # Solo gerentes y directores pueden editar empleados
    if not employee.can_edit_employees():
        return False
    
    # Si no se especifica empleado objetivo, verificar permisos generales
    if not target_employee:
        return True
    
    # Los directores pueden editar a cualquiera
    if employee.get_permission_level() == 'full':
        return True
    
    # Los gerentes pueden editar empleados de su departamento (excepto otros gerentes/directores)
    if (employee.get_permission_level() == 'management' and 
        employee.department == target_employee.department and
        target_employee.get_permission_level() not in ['management', 'full']):
        return True
    
    return False


def filter_employees_by_permissions(user, queryset):
    """
    Filtra un queryset de empleados según los permisos del usuario
    
    Args:
        user: Usuario que solicita los datos
        queryset: QuerySet de empleados
    
    Returns:
        QuerySet filtrado
    """
    if user.is_superuser:
        return queryset
    
    employee = get_employee_from_user(user)
    if not employee:
        return queryset.none()
    
    permission_level = employee.get_permission_level()
    
    if permission_level in ['full', 'management']:
        # Directores y gerentes ven todos los empleados
        return queryset
    elif permission_level == 'supervisor':
        # Supervisores ven empleados de su departamento
        return queryset.filter(department=employee.department)
    else:
        # Empleados básicos solo ven su propia información
        return queryset.filter(pk=employee.pk)


class EmployeePermissionMixin:
    """
    Mixin para vistas que manejan empleados con control de permisos
    """
    
    def get_queryset(self):
        """Filtra el queryset según los permisos del usuario"""
        queryset = super().get_queryset()
        return filter_employees_by_permissions(self.request.user, queryset)
    
    def dispatch(self, request, *args, **kwargs):
        """Verifica permisos antes de procesar la vista"""
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar si el usuario tiene permisos básicos
        employee = get_employee_from_user(request.user)
        if not employee and not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard:home')
        
        return super().dispatch(request, *args, **kwargs)


class AttendancePermissions:
    """Permisos específicos para el sistema de asistencias y GPS"""
    
    @staticmethod
    def can_view_location_maps(user):
        """Determina si puede ver mapas de ubicación"""
        if user.is_superuser or user.is_staff:
            return True
            
        employee = get_employee_from_user(user)
        if not employee:
            return False
            
        permission_level = employee.get_permission_level()
        # Incluir 'advanced' para empleados SENIOR que son directores/gerentes
        return permission_level in ['full', 'management', 'supervisor', 'advanced']
    
    @staticmethod
    def can_manage_work_areas(user):
        """Determina si puede gestionar áreas de trabajo"""
        if user.is_superuser or user.is_staff:
            return True
            
        employee = get_employee_from_user(user)
        if not employee:
            return False
            
        permission_level = employee.get_permission_level()
        # Incluir 'advanced' para empleados SENIOR con responsabilidades directivas
        return permission_level in ['full', 'management', 'advanced']
    
    @staticmethod
    def get_viewable_employees(user):
        """Obtiene empleados que el usuario puede ver"""
        from employees.models import Employee
        
        if user.is_superuser or user.is_staff:
            return Employee.objects.all()
            
        employee = get_employee_from_user(user)
        if not employee:
            return Employee.objects.none()
            
        permission_level = employee.get_permission_level()
        
        if permission_level in ['full']:
            # Directores ven todos
            return Employee.objects.all()
        elif permission_level in ['management']:
            # Gerentes ven su departamento
            return Employee.objects.filter(department=employee.department)
        elif permission_level in ['supervisor']:
            # Supervisores ven su equipo
            return Employee.objects.filter(
                department=employee.department,
                position__level__in=['ENTRY', 'JUNIOR', 'SENIOR']
            )
        else:
            # Empleados básicos solo se ven a sí mismos
            return Employee.objects.filter(pk=employee.pk)
