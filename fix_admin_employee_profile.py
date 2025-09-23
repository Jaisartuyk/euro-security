#!/usr/bin/env python
"""
Script para crear perfil de empleado para el usuario admin
EURO SECURITY - Fix Admin Employee Profile
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from departments.models import Department
from positions.models import Position

def main():
    print("🔧 Verificando y creando perfil de empleado para admin...")
    
    try:
        # Obtener usuario admin
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario admin encontrado: {admin_user.email}")
        
        # Verificar si ya tiene perfil de empleado
        try:
            employee = Employee.objects.get(user=admin_user)
            print(f"✅ Perfil de empleado ya existe: {employee.get_full_name()}")
            print(f"   - Departamento: {employee.department.name if employee.department else 'Sin departamento'}")
            print(f"   - Posición: {employee.position.title if employee.position else 'Sin posición'}")
            return
        except Employee.DoesNotExist:
            print("⚠️ No existe perfil de empleado para admin, creando...")
        
        # Obtener departamento administrativo
        try:
            admin_dept = Department.objects.get(code='ADM')
            print(f"✅ Departamento administrativo encontrado: {admin_dept.name}")
        except Department.DoesNotExist:
            print("❌ Departamento administrativo no encontrado, creando...")
            admin_dept = Department.objects.create(
                name='Administración',
                code='ADM',
                description='Departamento de Administración General',
                department_type='ADMINISTRATIVE'
            )
            print(f"✅ Departamento creado: {admin_dept.name}")
        
        # Obtener posición de director
        try:
            director_position = Position.objects.filter(level='DIRECTOR').first()
            if not director_position:
                print("❌ Posición de director no encontrada, creando...")
                director_position = Position.objects.create(
                    title='Director General',
                    code='DIR-GEN-001',
                    department=admin_dept,
                    level='DIRECTOR',
                    employment_type='FULL_TIME',
                    description='Director General de la empresa'
                )
                print(f"✅ Posición creada: {director_position.title}")
            else:
                print(f"✅ Posición de director encontrada: {director_position.title}")
        except Exception as e:
            print(f"❌ Error obteniendo posición: {e}")
            return
        
        # Crear perfil de empleado para admin
        employee = Employee.objects.create(
            user=admin_user,
            employee_id='EMP-ADMIN-001',
            first_name=admin_user.first_name or 'Administrador',
            last_name=admin_user.last_name or 'Sistema',
            email=admin_user.email,
            department=admin_dept,
            position=director_position,
            phone='0999999999',
            address='Oficina Principal',
            hire_date='2024-01-01',
            is_active=True
        )
        
        print(f"✅ Perfil de empleado creado exitosamente:")
        print(f"   - ID: {employee.employee_id}")
        print(f"   - Nombre: {employee.get_full_name()}")
        print(f"   - Email: {employee.email}")
        print(f"   - Departamento: {employee.department.name}")
        print(f"   - Posición: {employee.position.title}")
        print(f"   - Nivel: {employee.position.level}")
        
        # Verificar permisos
        print(f"\n🔐 Verificando permisos:")
        print(f"   - Nivel de permisos: {employee.get_permission_level()}")
        print(f"   - Es superusuario: {admin_user.is_superuser}")
        print(f"   - Es staff: {admin_user.is_staff}")
        
        print(f"\n✅ ¡Perfil de empleado configurado correctamente!")
        print(f"   Ahora el GPS tracking debería funcionar para el usuario admin.")
        
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado")
        print("   Ejecuta primero: python manage.py createsuperuser")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
