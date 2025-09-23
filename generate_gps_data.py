#!/usr/bin/env python3
"""
Script para generar datos GPS de prueba actuales
EURO SECURITY - Generate GPS Data
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

def generate_current_gps_data():
    """Generar datos GPS actuales para el mapa"""
    print("🛰️ EURO SECURITY - Generar Datos GPS Actuales")
    print("=" * 55)
    
    try:
        # Limpiar datos GPS antiguos
        old_records = GPSTracking.objects.filter(
            timestamp__lt=timezone.now() - timezone.timedelta(hours=2)
        )
        deleted_count = old_records.count()
        old_records.delete()
        print(f"🗑️ Eliminados {deleted_count} registros GPS antiguos")
        
        # Obtener empleados con áreas asignadas
        assignments = EmployeeWorkArea.objects.filter(is_active=True).select_related('employee', 'work_area')
        
        if not assignments.exists():
            print("❌ No hay empleados con áreas asignadas")
            return
        
        print(f"👥 Empleados con áreas asignadas: {assignments.count()}")
        
        # Generar ubicaciones GPS actuales
        current_time = timezone.now()
        created_count = 0
        
        for assignment in assignments:
            employee = assignment.employee
            work_area = assignment.work_area
            
            # Generar ubicación cerca del área de trabajo
            # 50% dentro del área, 50% fuera
            is_inside = random.choice([True, False])
            
            if is_inside:
                # Dentro del área (radio reducido)
                lat_offset = random.uniform(-0.0005, 0.0005)  # ~50m
                lng_offset = random.uniform(-0.0005, 0.0005)
            else:
                # Fuera del área (radio extendido)
                lat_offset = random.uniform(-0.003, 0.003)  # ~300m
                lng_offset = random.uniform(-0.003, 0.003)
            
            test_lat = float(work_area.latitude) + lat_offset
            test_lng = float(work_area.longitude) + lng_offset
            
            # Calcular si realmente está dentro del área
            distance = work_area.calculate_distance(test_lat, test_lng)
            is_within = distance <= (work_area.radius_meters + assignment.tolerance_meters)
            
            # Crear registro GPS actual
            gps_record = GPSTracking.objects.create(
                employee=employee,
                latitude=test_lat,
                longitude=test_lng,
                accuracy=random.randint(5, 25),
                tracking_type='AUTO',
                timestamp=current_time - timezone.timedelta(minutes=random.randint(0, 15)),
                work_area=work_area,
                is_within_work_area=is_within,
                distance_to_work_area=distance,
                battery_level=random.randint(60, 100),
                device_info='GPS Simulator - Real Time',
                notes=f'Ubicación actual - {work_area.name}',
                is_active_session=True
            )
            
            status = "✅ Dentro" if is_within else "⚠️ Fuera"
            print(f"   📍 {employee.get_full_name()}: {status} ({distance:.0f}m de {work_area.name})")
            created_count += 1
        
        print(f"\n🎯 RESUMEN:")
        print(f"   📊 Registros GPS creados: {created_count}")
        print(f"   🕐 Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   🛰️ Todos con is_active_session=True")
        
        # Verificar APIs
        print(f"\n🔌 VERIFICAR APIs:")
        print(f"   📡 /asistencia/api/rastreo-gps/ - Debería mostrar {created_count} empleados")
        print(f"   📍 /asistencia/api/areas-trabajo/ - Debería mostrar {WorkArea.objects.count()} áreas")
        
        # URLs para probar
        print(f"\n🌐 PROBAR MAPAS:")
        print(f"   🗺️ /asistencia/rastreo-tiempo-real/ - Mapa en tiempo real")
        print(f"   📊 /asistencia/mapa/ - Mapa de ubicaciones")
        
        # Datos para JavaScript
        print(f"\n📱 DATOS PARA JAVASCRIPT:")
        print(f"   Centro del mapa: -2.1894, -79.8890 (Guayaquil)")
        print(f"   Zoom recomendado: 12")
        print(f"   Empleados activos: {created_count}")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Ve a /asistencia/rastreo-tiempo-real/")
        print(f"   2. Deberías ver {created_count} marcadores en el mapa")
        print(f"   3. Marcadores verdes = dentro del área")
        print(f"   4. Marcadores amarillos = fuera del área")
        print(f"   5. Círculos azules = áreas de trabajo")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_current_gps_data()
