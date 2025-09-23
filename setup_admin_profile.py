#!/usr/bin/env python3
"""
Script para crear perfil de empleado para el superusuario
EURO SECURITY - Setup Admin Profile
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from departments.models import Department
from positions.models import Position

def setup_admin_profile():
    """Crear perfil de empleado para el superusuario"""
    print("🔧 EURO SECURITY - Configurar Perfil de Administrador")
    print("=" * 55)
    
    try:
        # Buscar superusuario
        admin_user = User.objects.filter(username='jairo').first()
        
        if not admin_user:
            print("❌ No se encontró el usuario 'jairo'")
            return
        
        print(f"👤 Usuario encontrado: {admin_user.username}")
        
        # Verificar si ya tiene perfil
        try:
            employee = Employee.objects.get(user=admin_user)
            print(f"✅ Ya tiene perfil de empleado: {employee.get_full_name()}")
            return
        except Employee.DoesNotExist:
            pass
        
        # Crear o buscar departamento de administración
        admin_dept, created = Department.objects.get_or_create(
            name="Administración",
            defaults={
                'description': 'Departamento de Administración General - EURO SECURITY',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Departamento creado: {admin_dept.name}")
        else:
            print(f"✅ Departamento encontrado: {admin_dept.name}")
        
        # Crear o buscar puesto de director
        director_position, created = Position.objects.get_or_create(
            title="Director General",
            defaults={
                'description': 'Director General de EURO SECURITY - Acceso completo al sistema',
                'level': 'full',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Puesto creado: {director_position.title}")
        else:
            print(f"✅ Puesto encontrado: {director_position.title}")
        
        # Crear perfil de empleado con todos los campos obligatorios
        employee = Employee.objects.create(
            user=admin_user,
            employee_id="ADMIN001",
            first_name="Jairo",
            last_name="Administrador",
            email=admin_user.email or "jairo1991st@hotmail.com",
            phone="000-000-0000",
            national_id="00000000",
            date_of_birth="1990-01-01",
            gender="M",
            marital_status="SINGLE",
            address="Oficina Principal EURO SECURITY",
            city="Ciudad",
            country="Colombia",
            department=admin_dept,
            position=director_position,
            hire_date="2024-01-01",
            current_salary=5000000.00,
            is_active=True
        )
        
        print(f"✅ Perfil de empleado creado: {employee.get_full_name()}")
        
        # Probar permisos
        from core.context_processors import attendance_permissions
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(admin_user)
        context = attendance_permissions(request)
        
        print(f"\n🔐 PERMISOS ACTIVADOS:")
        permissions = [
            ('can_view_attendance_dashboard', 'Dashboard de Asistencias'),
            ('can_view_attendance_reports', 'Reportes de Asistencia'),
            ('can_view_location_maps', 'Mapas de Ubicaciones'),
            ('can_export_reports', 'Exportar Datos CSV'),
        ]
        
        for key, desc in permissions:
            icon = "✅" if context.get(key, False) else "❌"
            print(f"   {icon} {desc}")
        
        print(f"   🎯 Nivel de permisos: {context.get('attendance_permission_level', 'none')}")
        
        print(f"\n🎯 MENÚ DISPONIBLE AHORA:")
        print(f"   👑 ADMINISTRACIÓN:")
        print(f"      ✅ Dashboard Administrativo")
        print(f"      ✅ Empleados")
        print(f"      ✅ Departamentos")
        print(f"      ✅ Puestos de Trabajo")
        print(f"      ✅ Reportes")
        
        print(f"   📊 CONTROL DE ASISTENCIAS:")
        print(f"      ✅ Dashboard Asistencias")
        print(f"      ✅ Reportes Generales")
        print(f"      ✅ Mapa de Ubicaciones")
        print(f"      ✅ Exportar Datos")
        print(f"      ✅ Marcación Manual")
        
        print(f"   👤 MI ASISTENCIA:")
        print(f"      ✅ Mi Historial")
        
        print(f"\n🚀 ¡LISTO! AHORA PUEDES:")
        print(f"   1. Actualizar la página web")
        print(f"   2. Ver el menú completo de Control de Asistencias")
        print(f"   3. Acceder a todas las funcionalidades:")
        print(f"      • Dashboard: /asistencia/dashboard/")
        print(f"      • Reportes: /asistencia/reportes/")
        print(f"      • Mapas: /asistencia/mapa/")
        print(f"      • Marcación: /asistencia/marcar/")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    setup_admin_profile()
