"""
Sistema de permisos para asistencias
EURO SECURITY - Attendance Permissions
"""
from django.db.models import Q
from employees.models import Employee
from departments.models import Department

class AttendancePermissions:
    """Manejo de permisos para visualización de asistencias"""
    
    @staticmethod
    def get_viewable_employees(user):
        """
        Retorna los empleados cuyas asistencias puede ver el usuario
        según su nivel jerárquico
        """
        # SUPERUSUARIOS: Acceso completo automático
        if user.is_superuser or user.is_staff:
            return Employee.objects.all()
            
        try:
            employee = Employee.objects.get(user=user)
            level = employee.position.level
            
            # DIRECTOR - Ve todos los empleados
            if level == 'full':
                return Employee.objects.all()
            
            # MANAGER - Ve su departamento y subordinados
            elif level == 'management':
                # Empleados del mismo departamento
                same_dept = Employee.objects.filter(department=employee.department)
                
                # Empleados de departamentos subordinados (si los hay)
                subordinate_depts = Department.objects.filter(
                    parent_department=employee.department
                )
                subordinate_employees = Employee.objects.filter(
                    department__in=subordinate_depts
                )
                
                return same_dept.union(subordinate_employees)
            
            # LEAD/SUPERVISOR - Ve su equipo directo
            elif level == 'supervisor':
                # Empleados del mismo departamento con nivel inferior
                return Employee.objects.filter(
                    department=employee.department,
                    position__level__in=['advanced', 'standard', 'basic']
                )
            
            # SENIOR - Ve empleados junior del mismo departamento
            elif level == 'advanced':
                return Employee.objects.filter(
                    department=employee.department,
                    position__level__in=['standard', 'basic']
                )
            
            # JUNIOR/ENTRY - Solo se ve a sí mismo
            else:
                return Employee.objects.filter(id=employee.id)
                
        except Employee.DoesNotExist:
            # Si no es empleado, no ve nada
            return Employee.objects.none()
    
    @staticmethod
    def can_view_employee_attendance(user, target_employee):
        """Verifica si el usuario puede ver la asistencia de un empleado específico"""
        viewable_employees = AttendancePermissions.get_viewable_employees(user)
        return target_employee in viewable_employees
    
    @staticmethod
    def get_viewable_departments(user):
        """Retorna los departamentos que puede ver el usuario"""
        # SUPERUSUARIOS: Acceso completo automático
        if user.is_superuser or user.is_staff:
            return Department.objects.all()
            
        try:
            employee = Employee.objects.get(user=user)
            
            # EXCEPCIÓN: Jefa de Operaciones puede ver Control de Calidad
            if employee.employee_id == 'EMP13807414':
                # Mayra Alejandra Espinoza Ponce - Jefa de Operaciones
                # Puede ver Operaciones + Control de Calidad
                return Department.objects.filter(
                    code__in=['OPE', 'CC']  # OPE = Operaciones, CC = Control de Calidad
                )
            
            level = employee.position.level
            
            # DIRECTOR - Ve todos los departamentos
            if level == 'full':
                return Department.objects.all()
            
            # MANAGER - Ve su departamento y subordinados
            elif level == 'management':
                departments = [employee.department]
                subordinate_depts = Department.objects.filter(
                    parent_department=employee.department
                )
                departments.extend(list(subordinate_depts))
                return Department.objects.filter(id__in=[d.id for d in departments])
            
            # LEAD/SUPERVISOR/SENIOR - Solo su departamento
            elif level in ['supervisor', 'advanced']:
                return Department.objects.filter(id=employee.department.id)
            
            # JUNIOR/ENTRY - No ve departamentos completos
            else:
                return Department.objects.none()
                
        except Employee.DoesNotExist:
            return Department.objects.none()
    
    @staticmethod
    def can_view_location_maps(user):
        """Verifica si el usuario puede ver mapas de ubicación"""
        # SUPERUSUARIOS: Acceso automático
        if user.is_superuser or user.is_staff:
            return True
            
        try:
            employee = Employee.objects.get(user=user)
            level = employee.position.level
            # Solo DIRECTOR, MANAGER y LEAD pueden ver mapas
            return level in ['full', 'management', 'supervisor']
        except Employee.DoesNotExist:
            return False
    
    @staticmethod
    def can_export_reports(user):
        """Verifica si el usuario puede exportar reportes"""
        # SUPERUSUARIOS: Acceso automático
        if user.is_superuser or user.is_staff:
            return True
            
        try:
            employee = Employee.objects.get(user=user)
            level = employee.position.level
            # Solo DIRECTOR y MANAGER pueden exportar
            return level in ['full', 'management']
        except Employee.DoesNotExist:
            return False
    
    @staticmethod
    def get_permission_level(user):
        """Retorna el nivel de permisos del usuario"""
        # SUPERUSUARIOS: Nivel máximo
        if user.is_superuser:
            return 'superuser'
        if user.is_staff:
            return 'staff'
            
        try:
            employee = Employee.objects.get(user=user)
            return employee.position.level
        except Employee.DoesNotExist:
            return 'none'
    
    @staticmethod
    def get_permission_description(user):
        """Retorna descripción de los permisos del usuario"""
        level = AttendancePermissions.get_permission_level(user)
        
        descriptions = {
            'full': 'Acceso completo - Ve todas las asistencias',
            'management': 'Gestión departamental - Ve su departamento y subordinados',
            'supervisor': 'Supervisión de equipo - Ve empleados de su departamento',
            'advanced': 'Acceso avanzado - Ve empleados junior de su departamento',
            'standard': 'Acceso estándar - Solo ve su propia asistencia',
            'basic': 'Acceso básico - Solo ve su propia asistencia',
            'none': 'Sin permisos de asistencia'
        }
        
        return descriptions.get(level, 'Permisos no definidos')

def attendance_permission_required(permission_level):
    """
    Decorador para vistas que requieren cierto nivel de permisos
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # SUPERUSUARIOS: Acceso automático sin restricciones
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            user_level = AttendancePermissions.get_permission_level(request.user)
            
            allowed_levels = {
                'full': ['full', 'superuser', 'staff'],
                'management': ['full', 'management', 'superuser', 'staff'],
                'supervisor': ['full', 'management', 'supervisor', 'superuser', 'staff'],
                'advanced': ['full', 'management', 'supervisor', 'advanced', 'superuser', 'staff'],
                'standard': ['full', 'management', 'supervisor', 'advanced', 'standard', 'superuser', 'staff'],
                'basic': ['full', 'management', 'supervisor', 'advanced', 'standard', 'basic', 'superuser', 'staff']
            }
            
            if user_level in allowed_levels.get(permission_level, []):
                return view_func(request, *args, **kwargs)
            else:
                from django.http import HttpResponseForbidden
                return HttpResponseForbidden("No tienes permisos para acceder a esta función")
        
        return wrapper
    return decorator
