#!/usr/bin/env python3
"""
Script para crear datos GPS de prueba inmediatos
EURO SECURITY - Create Test GPS Data
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models_gps import WorkArea, EmployeeWorkArea, GPSTracking
from employees.models import Employee
from departments.models import Department
from django.utils import timezone
from decimal import Decimal
import random

def create_test_data():
    """Crear datos GPS de prueba inmediatos"""
    print("🛰️ CREANDO DATOS GPS DE PRUEBA...")
    
    try:
        # 1. Usar empleados existentes
        employees = list(Employee.objects.filter(is_active=True)[:5])
        
        if not employees:
            print("❌ No hay empleados en el sistema.")
            print("💡 Crea empleados desde el admin de Django primero.")
            return False
        
        print(f"👥 Usando {len(employees)} empleados existentes:")
        for emp in employees:
            print(f"   - {emp.get_full_name()}")
        
        # 2. Crear áreas de trabajo en Guayaquil
        areas_data = [
            {
                "name": "Mall del Sol",
                "description": "Centro comercial principal",
                "latitude": Decimal("-2.1894"),
                "longitude": Decimal("-79.8890"),
                "radius_meters": 100,
                "area_type": "MALL"
            },
            {
                "name": "Centro Histórico",
                "description": "Zona histórica de Guayaquil",
                "latitude": Decimal("-2.1969"),
                "longitude": Decimal("-79.8862"),
                "radius_meters": 150,
                "area_type": "OTHER"
            },
            {
                "name": "Urdesa",
                "description": "Zona residencial",
                "latitude": Decimal("-2.1500"),
                "longitude": Decimal("-79.9000"),
                "radius_meters": 120,
                "area_type": "RESIDENTIAL"
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
        
        # 3. Asignar empleados a áreas
        for i, employee in enumerate(employees):
            if i < len(work_areas):
                assignment, created = EmployeeWorkArea.objects.get_or_create(
                    employee=employee,
                    work_area=work_areas[i],
                    defaults={
                        'tolerance_meters': 50,
                        'is_active': True
                    }
                )
                if created:
                    print(f"✅ Asignación: {employee.get_full_name()} → {work_areas[i].name}")
        
        # 4. Crear registros GPS actuales
        current_time = timezone.now()
        gps_records_created = 0
        
        for i, employee in enumerate(employees):
            if i < len(work_areas):
                work_area = work_areas[i]
                
                # Generar ubicación cerca del área (50% dentro, 50% fuera)
                is_inside = random.choice([True, False])
                
                if is_inside:
                    # Dentro del área
                    lat_offset = random.uniform(-0.0005, 0.0005)  # ~50m
                    lng_offset = random.uniform(-0.0005, 0.0005)
                else:
                    # Fuera del área
                    lat_offset = random.uniform(-0.002, 0.002)  # ~200m
                    lng_offset = random.uniform(-0.002, 0.002)
                
                test_lat = float(work_area.latitude) + lat_offset
                test_lng = float(work_area.longitude) + lng_offset
                
                # Calcular distancia
                distance = work_area.calculate_distance(test_lat, test_lng)
                is_within = distance <= (work_area.radius_meters + 50)  # +50m tolerancia
                
                # Crear registro GPS
                gps_record = GPSTracking.objects.create(
                    employee=employee,
                    latitude=test_lat,
                    longitude=test_lng,
                    accuracy=random.randint(5, 25),
                    tracking_type='AUTO',
                    timestamp=current_time - timezone.timedelta(minutes=random.randint(0, 10)),
                    work_area=work_area,
                    is_within_work_area=is_within,
                    distance_to_work_area=distance,
                    battery_level=random.randint(70, 100),
                    device_info='Test GPS Data',
                    notes=f'Ubicación de prueba - {work_area.name}',
                    is_active_session=True
                )
                
                status = "✅ Dentro" if is_within else "⚠️ Fuera"
                print(f"   📍 {employee.get_full_name()}: {status} ({distance:.0f}m de {work_area.name})")
                gps_records_created += 1
        
        print(f"\n🎯 RESUMEN:")
        print(f"   👥 Empleados: {len(employees)}")
        print(f"   🏢 Áreas de trabajo: {len(work_areas)}")
        print(f"   📍 Registros GPS: {gps_records_created}")
        print(f"   🕐 Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n🌐 AHORA PUEDES VER:")
        print(f"   🗺️ /asistencia/rastreo-tiempo-real/ - Mapa con {gps_records_created} empleados")
        print(f"   📊 /asistencia/mapa/ - Ubicaciones históricas")
        print(f"   🔌 /asistencia/api/rastreo-gps/ - API con datos JSON")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_test_data()
    if success:
        print(f"\n🎉 ¡DATOS GPS DE PRUEBA CREADOS EXITOSAMENTE!")
        print(f"🚀 Ve a /asistencia/rastreo-tiempo-real/ para ver el mapa funcionando")
    else:
        print(f"\n❌ Error creando datos de prueba")
