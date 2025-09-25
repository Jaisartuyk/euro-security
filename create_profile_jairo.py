#!/usr/bin/env python
import os
import django
import base64

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from attendance.models import FacialRecognitionProfile
from employees.models import Employee

def create_facial_profile_jairo():
    print('=== CREANDO PERFIL FACIAL PARA JAIRO ===')
    
    try:
        # Buscar el empleado EMP17517900
        employee = Employee.objects.get(employee_id='EMP17517900')
        print(f'✅ Empleado encontrado: {employee.get_full_name()}')
        
        # Crear o obtener perfil
        profile, created = FacialRecognitionProfile.objects.get_or_create(
            employee=employee,
            defaults={
                'face_encoding': base64.b64encode(b'dummy_encoding_for_jairo_production').decode('utf-8'),
                'confidence_threshold': 0.6,
                'is_active': True
            }
        )
        
        if created:
            print(f'✅ Perfil facial creado con ID: {profile.id}')
        else:
            print(f'ℹ️ Perfil facial ya existía con ID: {profile.id}')
            
        print(f'Umbral de confianza: {profile.confidence_threshold}')
        print(f'Estado: {"Activo" if profile.is_active else "Inactivo"}')
        
        # Verificar total de perfiles
        total_profiles = FacialRecognitionProfile.objects.count()
        print(f'Total de perfiles faciales: {total_profiles}')
        
    except Employee.DoesNotExist:
        print('❌ Empleado EMP17517900 no encontrado')
        # Listar empleados disponibles
        employees = Employee.objects.all()[:5]
        print('Empleados disponibles:')
        for emp in employees:
            print(f'  - {emp.employee_id}: {emp.get_full_name()}')
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_facial_profile_jairo()
