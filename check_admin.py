#!/usr/bin/env python3
"""
Script para verificar el superusuario existente
EURO SECURITY - Check Admin
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

def check_admin():
    """Verificar superusuario existente"""
    print("👑 EURO SECURITY - Verificar Administrador")
    print("=" * 50)
    
    try:
        # Buscar superusuarios
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            print("❌ No hay superusuarios en el sistema")
            return
        
        for admin_user in superusers:
            print(f"👤 Superusuario: {admin_user.username}")
            print(f"📧 Email: {admin_user.email}")
            print(f"👥 Nombre: {admin_user.get_full_name()}")
            print(f"🔑 Activo: {'✅' if admin_user.is_active else '❌'}")
            
            # Verificar si tiene perfil de empleado
            try:
                employee = Employee.objects.get(user=admin_user)
                print(f"✅ Tiene perfil de empleado: {employee.get_full_name()}")
                print(f"🏢 Departamento: {employee.department.name if employee.department else 'Sin departamento'}")
                print(f"💼 Puesto: {employee.position.title}")
                print(f"🎯 Nivel: {employee.position.get_level_display()}")
                
                # Probar permisos
                from core.context_processors import attendance_permissions
                
                class MockRequest:
                    def __init__(self, user):
                        self.user = user
                
                request = MockRequest(admin_user)
                context = attendance_permissions(request)
                
                print(f"\n🔐 PERMISOS DE ASISTENCIAS:")
                permissions = [
                    ('can_view_attendance_dashboard', 'Ver Dashboard'),
                    ('can_view_attendance_reports', 'Ver Reportes'),
                    ('can_view_location_maps', 'Ver Mapas'),
                    ('can_export_reports', 'Exportar Datos'),
                ]
                
                for key, desc in permissions:
                    icon = "✅" if context.get(key, False) else "❌"
                    print(f"   {icon} {desc}")
                
                print(f"   🎯 Nivel: {context.get('attendance_permission_level', 'none')}")
                
            except Employee.DoesNotExist:
                print("⚠️ El superusuario NO tiene perfil de empleado")
                print("🔧 Necesita crear un perfil de empleado para acceder a Control de Asistencias")
                
                # Ofrecer crear el perfil
                print(f"\n🛠️ CREAR PERFIL DE EMPLEADO:")
                print(f"   1. Necesitas un departamento y puesto con nivel 'full'")
                print(f"   2. Crear Employee asociado al superusuario")
                print(f"   3. Esto le dará acceso completo a Control de Asistencias")
                
                # Verificar si existen departamentos y puestos necesarios
                admin_dept = Department.objects.filter(name__icontains="admin").first()
                director_pos = Position.objects.filter(level='full').first()
                
                if not admin_dept:
                    print(f"   ⚠️ No hay departamento de administración")
                if not director_pos:
                    print(f"   ⚠️ No hay puesto con nivel 'full'")
            
            print("-" * 50)
        
        print(f"\n🎯 PARA ACCEDER AL CONTROL DE ASISTENCIAS:")
        print(f"   1. Inicia sesión con tu superusuario")
        print(f"   2. Si tienes perfil de empleado, verás el menú completo")
        print(f"   3. Si no tienes perfil, solo verás opciones básicas")
        print(f"   4. Ve a: http://127.0.0.1:8000/asistencia/reportes/")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_admin()
