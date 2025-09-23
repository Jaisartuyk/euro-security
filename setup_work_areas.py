#!/usr/bin/env python3
"""
Script para configurar áreas de trabajo y rastreo GPS
EURO SECURITY - Setup Work Areas
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
from django.utils import timezone
import random

def setup_work_areas():
    """Configurar áreas de trabajo para Guayaquil"""
    print("🗺️ EURO SECURITY - Configurar Áreas de Trabajo")
    print("=" * 55)
    
    try:
        # Áreas de trabajo en Guayaquil
        work_areas_data = [
            {
                'name': 'Mall del Sol - Seguridad',
                'description': 'Área de seguridad en Mall del Sol',
                'area_type': 'MALL',
                'latitude': -2.1709,
                'longitude': -79.9224,
                'radius_meters': 100,
                'address': 'Av. Juan Tanca Marengo, Guayaquil',
                'contact_person': 'Administración Mall del Sol',
                'contact_phone': '04-269-2677',
            },
            {
                'name': 'Centro Histórico - Patrullaje',
                'description': 'Zona de patrullaje en el centro histórico',
                'area_type': 'PATROL',
                'latitude': -2.1894,
                'longitude': -79.8890,
                'radius_meters': 200,
                'address': 'Malecón 2000, Guayaquil',
                'contact_person': 'Municipio de Guayaquil',
                'contact_phone': '04-259-4100',
            },
            {
                'name': 'Urdesa - Residencial',
                'description': 'Seguridad residencial en Urdesa',
                'area_type': 'RESIDENTIAL',
                'latitude': -2.1462,
                'longitude': -79.8882,
                'radius_meters': 150,
                'address': 'Urdesa Central, Guayaquil',
                'contact_person': 'Administración Urdesa',
                'contact_phone': '04-288-5500',
            },
            {
                'name': 'Las Peñas - Turístico',
                'description': 'Seguridad en zona turística Las Peñas',
                'area_type': 'OTHER',
                'latitude': -2.2180,
                'longitude': -79.8862,
                'radius_meters': 80,
                'address': 'Barrio Las Peñas, Guayaquil',
                'contact_person': 'Ministerio de Turismo',
                'contact_phone': '04-256-8764',
            },
            {
                'name': 'Kennedy Norte - Comercial',
                'description': 'Seguridad en zona comercial Kennedy Norte',
                'area_type': 'BUILDING',
                'latitude': -2.1304,
                'longitude': -79.8890,
                'radius_meters': 120,
                'address': 'Av. Francisco de Orellana, Kennedy Norte',
                'contact_person': 'Cámara de Comercio',
                'contact_phone': '04-268-2671',
            },
        ]
        
        created_areas = []
        
        # Crear áreas de trabajo
        for area_data in work_areas_data:
            area, created = WorkArea.objects.get_or_create(
                name=area_data['name'],
                defaults=area_data
            )
            
            if created:
                print(f"✅ Área creada: {area.name}")
            else:
                print(f"✅ Área existente: {area.name}")
            
            created_areas.append(area)
        
        # Asignar empleados a áreas de trabajo
        employees = Employee.objects.all()[:5]  # Primeros 5 empleados
        
        if employees:
            print(f"\n👥 Asignando empleados a áreas de trabajo:")
            
            for i, employee in enumerate(employees):
                # Asignar área principal
                primary_area = created_areas[i % len(created_areas)]
                
                assignment, created = EmployeeWorkArea.objects.get_or_create(
                    employee=employee,
                    work_area=primary_area,
                    defaults={
                        'is_primary': True,
                        'tolerance_meters': 20,
                        'monday': True,
                        'tuesday': True,
                        'wednesday': True,
                        'thursday': True,
                        'friday': True,
                        'saturday': False,
                        'sunday': False,
                    }
                )
                
                if created:
                    print(f"   ✅ {employee.get_full_name()} → {primary_area.name}")
                else:
                    print(f"   ✅ {employee.get_full_name()} ya asignado a {primary_area.name}")
                
                # Crear ubicación GPS de prueba
                create_test_gps_location(employee, primary_area)
        
        print(f"\n🎯 RESUMEN:")
        print(f"   📍 Áreas creadas: {len(created_areas)}")
        print(f"   👥 Empleados asignados: {employees.count()}")
        print(f"   🗺️ Ubicaciones GPS generadas: {employees.count()}")
        
        print(f"\n🌐 URLS DISPONIBLES:")
        print(f"   📊 Rastreo en tiempo real: /asistencia/rastreo-tiempo-real/")
        print(f"   🗺️ Mapa de ubicaciones: /asistencia/mapa/")
        print(f"   ⚠️ Alertas de ubicación: /asistencia/alertas-ubicacion/")
        
        print(f"\n🎯 FUNCIONALIDADES ACTIVAS:")
        print(f"   ✅ Áreas de trabajo definidas geográficamente")
        print(f"   ✅ Empleados asignados a áreas específicas")
        print(f"   ✅ Rastreo GPS en tiempo real")
        print(f"   ✅ Validación de ubicación al marcar asistencia")
        print(f"   ✅ Alertas automáticas por salir del área")
        print(f"   ✅ Monitoreo de movimientos y avance")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Ve a /asistencia/rastreo-tiempo-real/")
        print(f"   2. Verás empleados en tiempo real en el mapa")
        print(f"   3. Las áreas aparecen como círculos azules")
        print(f"   4. Los empleados aparecen como puntos verdes/amarillos")
        print(f"   5. Verde = dentro del área, Amarillo = fuera del área")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def create_test_gps_location(employee, work_area):
    """Crear ubicación GPS de prueba para un empleado"""
    
    # Generar ubicación cerca del área de trabajo
    lat_offset = random.uniform(-0.002, 0.002)  # ~200m de variación
    lng_offset = random.uniform(-0.002, 0.002)
    
    test_lat = float(work_area.latitude) + lat_offset
    test_lng = float(work_area.longitude) + lng_offset
    
    # Determinar si está dentro del área
    distance = work_area.calculate_distance(test_lat, test_lng)
    is_within = distance <= work_area.radius_meters
    
    # Crear registro GPS
    GPSTracking.objects.create(
        employee=employee,
        latitude=test_lat,
        longitude=test_lng,
        accuracy=random.randint(5, 25),
        tracking_type='AUTO',
        work_area=work_area,
        is_within_work_area=is_within,
        distance_to_work_area=distance,
        battery_level=random.randint(60, 100),
        device_info='Test Device - GPS Simulator',
        notes=f'Ubicación de prueba - {work_area.name}',
        is_active_session=True
    )

if __name__ == "__main__":
    setup_work_areas()
