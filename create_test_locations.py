#!/usr/bin/env python3
"""
Script para crear ubicaciones de prueba en el mapa
EURO SECURITY - Create Test Locations
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models import AttendanceRecord
from employees.models import Employee
from django.utils import timezone
from datetime import datetime, timedelta
import random

def create_test_locations():
    """Crear ubicaciones de prueba para el mapa"""
    print("📍 EURO SECURITY - Crear Ubicaciones de Prueba")
    print("=" * 50)
    
    try:
        # Buscar empleados
        employees = Employee.objects.all()[:5]  # Primeros 5 empleados
        
        if not employees:
            print("❌ No hay empleados en el sistema")
            return
        
        print(f"👥 Empleados encontrados: {employees.count()}")
        
        # Ubicaciones de prueba en Guayaquil, Ecuador
        test_locations = [
            {"lat": -2.1894, "lng": -79.8890, "name": "Centro de Guayaquil"},
            {"lat": -2.1709, "lng": -79.9224, "name": "Mall del Sol"},
            {"lat": -2.1462, "lng": -79.8882, "name": "Urdesa"},
            {"lat": -2.2180, "lng": -79.8862, "name": "Las Peñas"},
            {"lat": -2.1304, "lng": -79.8890, "name": "Kennedy Norte"},
        ]
        
        # Crear registros de prueba para hoy
        today = timezone.now().date()
        created_count = 0
        
        for i, employee in enumerate(employees):
            # Seleccionar ubicación
            location = test_locations[i % len(test_locations)]
            
            # Crear entrada
            entry_time = timezone.now().replace(
                hour=random.randint(7, 9),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            
            entry_record = AttendanceRecord.objects.create(
                employee=employee,
                attendance_type='IN',
                timestamp=entry_time,
                verification_method='EMERGENCY',
                latitude=location['lat'] + random.uniform(-0.01, 0.01),  # Pequeña variación
                longitude=location['lng'] + random.uniform(-0.01, 0.01),
                location_accuracy=random.randint(5, 20),
                address=f"{location['name']} - EURO SECURITY Guayaquil",
                facial_confidence=random.randint(85, 98),
                device_info='Test Device',
                is_valid=True,
                notes=f'Registro de prueba - {location["name"]}'
            )
            created_count += 1
            
            # Crear salida (50% de probabilidad)
            if random.choice([True, False]):
                exit_time = entry_time + timedelta(hours=random.randint(6, 10))
                
                exit_record = AttendanceRecord.objects.create(
                    employee=employee,
                    attendance_type='OUT',
                    timestamp=exit_time,
                    verification_method='EMERGENCY',
                    latitude=location['lat'] + random.uniform(-0.01, 0.01),
                    longitude=location['lng'] + random.uniform(-0.01, 0.01),
                    location_accuracy=random.randint(5, 20),
                    address=f"{location['name']} - EURO SECURITY Guayaquil",
                    facial_confidence=random.randint(85, 98),
                    device_info='Test Device',
                    is_valid=True,
                    notes=f'Salida de prueba - {location["name"]}'
                )
                created_count += 1
            
            print(f"✅ {employee.get_full_name()}: {location['name']}")
        
        print(f"\n🎯 RESUMEN:")
        print(f"   📊 Registros creados: {created_count}")
        print(f"   📅 Fecha: {today}")
        print(f"   🗺️ Ubicaciones: {len(test_locations)} zonas de Guayaquil")
        
        print(f"\n🌐 AHORA PUEDES:")
        print(f"   1. Ve a: /asistencia/mapa/")
        print(f"   2. Deberías ver marcadores en el mapa")
        print(f"   3. Cada marcador muestra información del empleado")
        print(f"   4. Los colores indican el tipo de marcación:")
        print(f"      🟢 Verde: Entrada")
        print(f"      🔴 Rojo: Salida")
        print(f"      🔵 Azul: Descanso")
        
        print(f"\n📍 UBICACIONES DE PRUEBA:")
        for loc in test_locations:
            print(f"   • {loc['name']}: {loc['lat']}, {loc['lng']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_locations()
