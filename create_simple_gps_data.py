#!/usr/bin/env python3
"""
Script simple para crear datos GPS básicos
EURO SECURITY - Simple GPS Data
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models_gps import WorkArea, GPSTracking
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import random

def create_simple_data():
    """Crear datos GPS básicos para mostrar en el mapa"""
    print("🛰️ CREANDO DATOS GPS BÁSICOS...")
    
    try:
        # 1. Crear áreas de trabajo básicas
        areas_data = [
            {
                "name": "Mall del Sol",
                "description": "Centro comercial",
                "latitude": Decimal("-2.1894"),
                "longitude": Decimal("-79.8890"),
                "radius_meters": 100,
                "area_type": "MALL"
            },
            {
                "name": "Centro Histórico", 
                "description": "Zona histórica",
                "latitude": Decimal("-2.1969"),
                "longitude": Decimal("-79.8862"),
                "radius_meters": 150,
                "area_type": "OTHER"
            }
        ]
        
        work_areas = []
        for area_data in areas_data:
            area, created = WorkArea.objects.get_or_create(
                name=area_data["name"],
                defaults=area_data
            )
            work_areas.append(area)
            if created:
                print(f"✅ Área creada: {area.name}")
        
        # 2. Crear registros GPS simulados
        current_time = timezone.now()
        gps_records_created = 0
        
        # Obtener o crear empleado basado en superusuario
        superuser = User.objects.filter(is_superuser=True).first()
        
        if not superuser:
            print("❌ No hay superusuario. Crea uno primero con 'python manage.py createsuperuser'")
            return False
        
        # Buscar empleado asociado al superusuario
        from employees.models import Employee
        try:
            employee = Employee.objects.get(user=superuser)
            print(f"👤 Usando empleado: {employee.get_full_name()}")
        except Employee.DoesNotExist:
            # Crear empleado básico para el superusuario
            from departments.models import Department
            from positions.models import Position
            
            # Crear departamento básico si no existe
            dept, _ = Department.objects.get_or_create(
                name="Administración",
                defaults={'description': 'Departamento administrativo', 'is_active': True}
            )
            
            # Crear posición básica si no existe
            pos, _ = Position.objects.get_or_create(
                title="Administrador",
                defaults={
                    'description': 'Administrador del sistema',
                    'department': dept,
                    'level': 'full',
                    'is_active': True
                }
            )
            
            # Crear empleado básico
            from datetime import date
            employee = Employee.objects.create(
                employee_id=f"EMP-{superuser.id:04d}",
                user=superuser,
                first_name=superuser.first_name or "Admin",
                last_name=superuser.last_name or "Usuario",
                email=superuser.email,
                phone="0999999999",
                national_id="9999999999",
                date_of_birth=date(1990, 1, 1),
                gender='M',
                marital_status='SINGLE',
                address="Dirección de prueba",
                city="Guayaquil",
                country="Ecuador",
                department=dept,
                position=pos,
                hire_date=date.today(),
                current_salary=1000.00,
                is_active=True
            )
            print(f"✅ Empleado creado: {employee.get_full_name()}")
        
        # Crear registros GPS para cada área
        for i, work_area in enumerate(work_areas):
            # Generar ubicación cerca del área
            lat_offset = random.uniform(-0.001, 0.001)  # ~100m
            lng_offset = random.uniform(-0.001, 0.001)
            
            test_lat = float(work_area.latitude) + lat_offset
            test_lng = float(work_area.longitude) + lng_offset
            
            # Calcular distancia
            distance = work_area.calculate_distance(test_lat, test_lng)
            is_within = distance <= work_area.radius_meters
            
            # Crear registro GPS básico
            gps_record = GPSTracking.objects.create(
                employee=employee,  # Usar empleado creado
                latitude=test_lat,
                longitude=test_lng,
                accuracy=random.randint(5, 25),
                tracking_type='AUTO',
                timestamp=current_time - timezone.timedelta(minutes=random.randint(0, 30)),
                work_area=work_area,
                is_within_work_area=is_within,
                distance_to_work_area=distance,
                battery_level=random.randint(70, 100),
                device_info='Datos de prueba GPS',
                notes=f'Ubicación simulada - {work_area.name}',
                is_active_session=True
            )
            
            status = "✅ Dentro" if is_within else "⚠️ Fuera"
            print(f"   📍 Ubicación {i+1}: {status} ({distance:.0f}m de {work_area.name})")
            gps_records_created += 1
        
        # 3. Crear ubicación actual del usuario (basada en GPS real capturado)
        user_lat = -2.2485  # Coordenada capturada del GPS
        user_lng = -79.8893
        
        current_gps = GPSTracking.objects.create(
            employee=employee,
            latitude=user_lat,
            longitude=user_lng,
            accuracy=10,
            tracking_type='AUTO',
            timestamp=current_time,
            work_area=None,
            is_within_work_area=False,
            distance_to_work_area=0,
            battery_level=85,
            device_info='Usuario actual',
            notes='Ubicación actual del usuario',
            is_active_session=True
        )
        gps_records_created += 1
        print(f"   📍 Tu ubicación actual: {user_lat}, {user_lng}")
        
        print(f"\n🎯 RESUMEN:")
        print(f"   🏢 Áreas de trabajo: {len(work_areas)}")
        print(f"   📍 Registros GPS: {gps_records_created}")
        print(f"   🕐 Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n🌐 AHORA DEBERÍAS VER:")
        print(f"   🗺️ /asistencia/rastreo-tiempo-real/ - Mapa con {gps_records_created} ubicaciones")
        print(f"   📊 /asistencia/mapa/ - Ubicaciones en el mapa")
        print(f"   🔌 /asistencia/api/rastreo-gps/ - API con datos JSON")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_simple_data()
    if success:
        print(f"\n🎉 ¡DATOS GPS BÁSICOS CREADOS!")
        print(f"🚀 Recarga la página del mapa para ver los datos")
    else:
        print(f"\n❌ Error creando datos básicos")
