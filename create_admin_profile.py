#!/usr/bin/env python
"""
Script para crear perfil de empleado para el superusuario jairo
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee
from departments.models import Department
from positions.models import Position
from datetime import date

def create_admin_profile():
    try:
        # Obtener el usuario jairo
        user = User.objects.get(username='jairo')
        print(f"✅ Usuario encontrado: {user.username}")
        
        # Verificar si ya tiene perfil
        try:
            existing = Employee.objects.get(user=user)
            print(f"⚠️ Ya existe perfil: {existing.employee_id}")
            return existing
        except Employee.DoesNotExist:
            pass
        
        # Obtener departamento de Administración
        try:
            department = Department.objects.get(code='ADM')
            print(f"✅ Departamento encontrado: {department.name}")
        except Department.DoesNotExist:
            print("❌ Departamento ADM no encontrado")
            return None
        
        # Buscar posición de DIRECTOR
        try:
            position = Position.objects.filter(level='DIRECTOR').first()
            if not position:
                # Si no hay DIRECTOR, buscar MANAGER
                position = Position.objects.filter(level='MANAGER').first()
            if not position:
                print("❌ No se encontró posición de alto rango")
                return None
            print(f"✅ Posición encontrada: {position.title}")
        except Exception as e:
            print(f"❌ Error buscando posición: {e}")
            return None
        
        # Crear perfil de empleado
        employee = Employee.objects.create(
            user=user,
            employee_id='CEO001',
            first_name='Jairo',
            last_name='Sánchez Triana',
            email='jairo1991st@hotmail.com',
            phone='+593-99-123-4567',
            national_id='1234567890',
            date_of_birth=date(1991, 1, 1),
            gender='M',
            marital_status='SINGLE',
            address='Av. Principal 123, Centro Empresarial',
            city='Guayaquil',
            country='Ecuador',
            department=department,
            position=position,
            hire_date=date(2024, 1, 1),
            current_salary=8000.00,
            is_active=True
        )
        
        print(f"🎉 Perfil creado exitosamente: {employee.employee_id} - {employee.get_full_name()}")
        print(f"📊 Nivel de permisos: {employee.get_permission_level()}")
        return employee
        
    except User.DoesNotExist:
        print("❌ Usuario 'jairo' no encontrado")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == '__main__':
    create_admin_profile()
