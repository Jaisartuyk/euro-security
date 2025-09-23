#!/usr/bin/env python3
"""
Script para probar el sistema de permisos de asistencias
EURO SECURITY - Test Permissions
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.permissions import AttendancePermissions
from employees.models import Employee
from django.contrib.auth.models import User

def test_permissions():
    """Probar sistema de permisos"""
    print("🔐 EURO SECURITY - Test Sistema de Permisos")
    print("=" * 50)
    
    try:
        # Buscar empleado de prueba
        employee = Employee.objects.get(first_name="JAIRO JAVIER", last_name="SANCHEZ TRIANA")
        user = employee.user
        
        print(f"👤 Usuario de prueba: {employee.get_full_name()}")
        print(f"🏢 Departamento: {employee.department.name if employee.department else 'Sin departamento'}")
        print(f"💼 Puesto: {employee.position.title}")
        print(f"🎯 Nivel: {employee.position.get_level_display()}")
        
        # Probar permisos
        print(f"\n🔐 PERMISOS DEL USUARIO:")
        print(f"   Nivel de permisos: {AttendancePermissions.get_permission_level(user)}")
        print(f"   Descripción: {AttendancePermissions.get_permission_description(user)}")
        
        # Empleados que puede ver
        viewable_employees = AttendancePermissions.get_viewable_employees(user)
        print(f"\n👥 EMPLEADOS QUE PUEDE VER:")
        print(f"   Total: {viewable_employees.count()}")
        for emp in viewable_employees[:5]:  # Mostrar solo los primeros 5
            print(f"   - {emp.get_full_name()} ({emp.department.name if emp.department else 'Sin dept'})")
        if viewable_employees.count() > 5:
            print(f"   ... y {viewable_employees.count() - 5} más")
        
        # Departamentos que puede ver
        viewable_departments = AttendancePermissions.get_viewable_departments(user)
        print(f"\n🏢 DEPARTAMENTOS QUE PUEDE VER:")
        print(f"   Total: {viewable_departments.count()}")
        for dept in viewable_departments:
            print(f"   - {dept.name}")
        
        # Permisos específicos
        print(f"\n🎯 PERMISOS ESPECÍFICOS:")
        print(f"   Ver mapas: {'✅' if AttendancePermissions.can_view_location_maps(user) else '❌'}")
        print(f"   Exportar reportes: {'✅' if AttendancePermissions.can_export_reports(user) else '❌'}")
        
        # URLs disponibles
        print(f"\n🌐 URLS DISPONIBLES:")
        print(f"   /asistencia/reportes/ - Reportes generales")
        print(f"   /asistencia/mapa/ - Mapa de ubicaciones")
        for dept in viewable_departments:
            print(f"   /asistencia/reportes/departamento/{dept.id}/ - Reporte de {dept.name}")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"   1. Inicia el servidor: python manage.py runserver")
        print(f"   2. Ve a /asistencia/reportes/")
        print(f"   3. Deberías ver reportes según tus permisos")
        print(f"   4. Prueba el mapa en /asistencia/mapa/")
        
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_permissions()
