#!/usr/bin/env python3
"""
Script para crear perfil de empleado para el superusuario (versión corregida)
EURO SECURITY - Fix Admin Profile
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

def fix_admin_profile():
    """Crear perfil de empleado para el superusuario (versión corregida)"""
    print("🔧 EURO SECURITY - Corregir Perfil de Administrador")
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
            print(f"🏢 Departamento: {employee.department.name}")
            print(f"💼 Puesto: {employee.position.title}")
            print(f"🎯 Nivel: {employee.position.get_level_display()}")
            
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
            
            print(f"\n🚀 ¡PERFIL YA CONFIGURADO!")
            print(f"   Puedes acceder a todas las funcionalidades de Control de Asistencias")
            return
            
        except Employee.DoesNotExist:
            pass
        
        # Buscar departamento y puesto
        admin_dept = Department.objects.filter(name="Administración").first()
        director_position = Position.objects.filter(title="Director General").first()
        
        if not admin_dept or not director_position:
            print("❌ Faltan departamento o puesto. Ejecuta setup_admin_profile.py primero")
            return
        
        # Verificar si el email ya existe
        existing_email = Employee.objects.filter(email=admin_user.email).first()
        if existing_email:
            print(f"⚠️ Email {admin_user.email} ya está en uso por otro empleado")
            # Usar un email único
            admin_email = f"admin.{admin_user.username}@eurosecurity.com"
        else:
            admin_email = admin_user.email or "jairo1991st@hotmail.com"
        
        # Verificar si el national_id ya existe
        national_id = "00000001"  # Diferente al anterior
        while Employee.objects.filter(national_id=national_id).exists():
            national_id = f"0000000{len(Employee.objects.all()) + 1}"
        
        # Verificar si el employee_id ya existe
        employee_id = "ADMIN001"
        counter = 1
        while Employee.objects.filter(employee_id=employee_id).exists():
            counter += 1
            employee_id = f"ADMIN{counter:03d}"
        
        print(f"🔧 Creando perfil con:")
        print(f"   📧 Email: {admin_email}")
        print(f"   🆔 Employee ID: {employee_id}")
        print(f"   📄 National ID: {national_id}")
        
        # Crear perfil de empleado
        employee = Employee.objects.create(
            user=admin_user,
            employee_id=employee_id,
            first_name="Jairo",
            last_name="Administrador",
            email=admin_email,
            phone="000-000-0000",
            national_id=national_id,
            date_of_birth="1990-01-01",
            gender="M",
            marital_status="SINGLE",
            address="Oficina Principal EURO SECURITY - Centro de Guayaquil",
            city="Guayaquil",
            country="Ecuador",
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
        print(f"   📊 CONTROL DE ASISTENCIAS:")
        print(f"      ✅ Dashboard Asistencias")
        print(f"      ✅ Reportes Generales")
        print(f"      ✅ Mapa de Ubicaciones")
        print(f"      ✅ Exportar Datos")
        print(f"      ✅ Marcación Manual")
        
        print(f"\n🚀 ¡LISTO! AHORA PUEDES:")
        print(f"   1. Actualizar la página web (F5)")
        print(f"   2. Ver el menú completo de 'CONTROL DE ASISTENCIAS'")
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
    fix_admin_profile()
