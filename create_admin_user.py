#!/usr/bin/env python3
"""
Script para crear usuario administrador con acceso completo
EURO SECURITY - Create Admin User
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

def create_admin_user():
    """Crear usuario administrador"""
    print("👑 EURO SECURITY - Crear Usuario Administrador")
    print("=" * 50)
    
    try:
        # Verificar si ya existe un superusuario
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if admin_user:
            print(f"✅ Ya existe un superusuario: {admin_user.username}")
            
            # Verificar si tiene perfil de empleado
            try:
                employee = Employee.objects.get(user=admin_user)
                print(f"👤 Perfil de empleado: {employee.get_full_name()}")
                print(f"🏢 Departamento: {employee.department.name if employee.department else 'Sin departamento'}")
                print(f"💼 Puesto: {employee.position.title}")
                print(f"🎯 Nivel: {employee.position.get_level_display()}")
            except Employee.DoesNotExist:
                print("⚠️ El superusuario no tiene perfil de empleado")
                
                # Crear perfil de empleado para el admin
                print("🔧 Creando perfil de empleado para el administrador...")
                
                # Buscar o crear departamento de administración
                admin_dept, created = Department.objects.get_or_create(
                    name="Administración",
                    defaults={
                        'description': 'Departamento de Administración General',
                        'is_active': True
                    }
                )
                if created:
                    print(f"✅ Departamento creado: {admin_dept.name}")
                
                # Buscar o crear puesto de director
                director_position, created = Position.objects.get_or_create(
                    title="Director General",
                    defaults={
                        'description': 'Director General de EURO SECURITY',
                        'level': 'full',
                        'is_active': True
                    }
                )
                if created:
                    print(f"✅ Puesto creado: {director_position.title}")
                
                # Crear perfil de empleado
                employee = Employee.objects.create(
                    user=admin_user,
                    first_name="Administrador",
                    last_name="Sistema",
                    email=admin_user.email or "admin@eurosecurity.com",
                    phone="000-000-0000",
                    department=admin_dept,
                    position=director_position,
                    hire_date="2024-01-01",
                    is_active=True
                )
                print(f"✅ Perfil de empleado creado: {employee.get_full_name()}")
        
        else:
            print("🔧 Creando nuevo superusuario...")
            
            # Crear superusuario
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@eurosecurity.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema'
            )
            print(f"✅ Superusuario creado: {admin_user.username}")
            
            # Crear departamento y puesto si no existen
            admin_dept, created = Department.objects.get_or_create(
                name="Administración",
                defaults={
                    'description': 'Departamento de Administración General',
                    'is_active': True
                }
            )
            
            director_position, created = Position.objects.get_or_create(
                title="Director General",
                defaults={
                    'description': 'Director General de EURO SECURITY',
                    'level': 'full',
                    'is_active': True
                }
            )
            
            # Crear perfil de empleado
            employee = Employee.objects.create(
                user=admin_user,
                first_name="Administrador",
                last_name="Sistema",
                email="admin@eurosecurity.com",
                phone="000-000-0000",
                department=admin_dept,
                position=director_position,
                hire_date="2024-01-01",
                is_active=True
            )
            print(f"✅ Perfil de empleado creado: {employee.get_full_name()}")
        
        # Probar permisos del administrador
        from core.context_processors import attendance_permissions
        
        class MockRequest:
            def __init__(self, user):
                self.user = user
        
        request = MockRequest(admin_user)
        context = attendance_permissions(request)
        
        print(f"\n🔐 PERMISOS DEL ADMINISTRADOR:")
        for key, value in context.items():
            icon = "✅" if value else "❌"
            print(f"   {icon} {key}: {value}")
        
        print(f"\n🎯 MENÚ DISPONIBLE PARA ADMINISTRADOR:")
        print(f"   👑 ADMINISTRACIÓN COMPLETA:")
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
        
        print(f"\n🎯 CREDENCIALES DE ACCESO:")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin123")
        print(f"   URL: http://127.0.0.1:8000/login/")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Inicia sesión como administrador")
        print(f"   2. Verás el menú completo de Control de Asistencias")
        print(f"   3. Prueba todas las funcionalidades:")
        print(f"      - Dashboard de Asistencias")
        print(f"      - Reportes Departamentales")
        print(f"      - Mapa de Ubicaciones con Google Maps")
        print(f"      - Exportación de datos CSV")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_admin_user()
