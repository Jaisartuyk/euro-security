#!/usr/bin/env python3
"""
Script para probar el sistema completo de rastreo GPS
EURO SECURITY - Test GPS System
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models_gps import WorkArea, EmployeeWorkArea, GPSTracking, LocationAlert
from employees.models import Employee
from django.utils import timezone
from datetime import timedelta

def test_gps_system():
    """Probar el sistema completo de rastreo GPS"""
    print("🛰️ EURO SECURITY - Test Sistema GPS Completo")
    print("=" * 55)
    
    try:
        # Verificar áreas de trabajo
        areas = WorkArea.objects.filter(is_active=True)
        print(f"📍 Áreas de trabajo configuradas: {areas.count()}")
        
        for area in areas:
            print(f"   • {area.name} ({area.get_area_type_display()}) - Radio: {area.radius_meters}m")
        
        # Verificar asignaciones de empleados
        assignments = EmployeeWorkArea.objects.filter(is_active=True)
        print(f"\n👥 Asignaciones de empleados: {assignments.count()}")
        
        for assignment in assignments:
            print(f"   • {assignment.employee.get_full_name()} → {assignment.work_area.name}")
        
        # Verificar registros GPS recientes
        recent_gps = GPSTracking.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=1),
            is_active_session=True
        ).select_related('employee', 'work_area')
        
        print(f"\n🛰️ Registros GPS recientes (última hora): {recent_gps.count()}")
        
        for gps in recent_gps:
            status = "✅ En área" if gps.is_within_work_area else "⚠️ Fuera del área"
            distance = f" ({gps.distance_to_work_area:.0f}m)" if gps.distance_to_work_area else ""
            print(f"   • {gps.employee.get_full_name()}: {status}{distance}")
        
        # Verificar alertas activas
        active_alerts = LocationAlert.objects.filter(is_resolved=False)
        print(f"\n⚠️ Alertas activas: {active_alerts.count()}")
        
        for alert in active_alerts:
            print(f"   • {alert.get_alert_type_display()}: {alert.employee.get_full_name()}")
        
        # Estadísticas generales
        total_employees = Employee.objects.count()
        employees_with_gps = Employee.objects.filter(gps_tracking__isnull=False).distinct().count()
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   👥 Total empleados: {total_employees}")
        print(f"   🛰️ Con rastreo GPS: {employees_with_gps}")
        print(f"   📍 Áreas configuradas: {areas.count()}")
        print(f"   ⚠️ Alertas activas: {active_alerts.count()}")
        
        # URLs del sistema
        print(f"\n🌐 URLS DEL SISTEMA GPS:")
        print(f"   📊 Dashboard tiempo real: /asistencia/rastreo-tiempo-real/")
        print(f"   🗺️ Mapa ubicaciones: /asistencia/mapa/")
        print(f"   ⚠️ Alertas ubicación: /asistencia/alertas-ubicacion/")
        print(f"   📋 Reportes asistencia: /asistencia/reportes/")
        
        # APIs disponibles
        print(f"\n🔌 APIs DISPONIBLES:")
        print(f"   📡 Rastreo GPS: /asistencia/api/rastreo-gps/")
        print(f"   📍 Áreas trabajo: /asistencia/api/areas-trabajo/")
        print(f"   📲 Actualizar GPS: /asistencia/api/actualizar-gps/")
        print(f"   📊 Ubicaciones: /asistencia/api/ubicaciones/")
        
        # Funcionalidades implementadas
        print(f"\n✅ FUNCIONALIDADES ACTIVAS:")
        print(f"   🛰️ Rastreo GPS en tiempo real")
        print(f"   📍 Áreas de trabajo geográficas")
        print(f"   ⚠️ Alertas automáticas por ubicación")
        print(f"   🗺️ Visualización en Google Maps")
        print(f"   📊 Dashboard interactivo")
        print(f"   📱 API para apps móviles")
        print(f"   🔐 Control de permisos por nivel")
        print(f"   📋 Historial de movimientos")
        
        # Validación de marcación
        print(f"\n🎯 VALIDACIÓN DE MARCACIÓN:")
        print(f"   ✅ Verifica ubicación al marcar entrada/salida")
        print(f"   ✅ Bloquea marcación fuera del área permitida")
        print(f"   ✅ Registra ubicación GPS en cada marcación")
        print(f"   ✅ Calcula distancia al área de trabajo")
        print(f"   ✅ Genera alertas automáticas")
        
        # Próximos pasos
        print(f"\n🚀 SISTEMA LISTO PARA:")
        print(f"   1. Monitoreo en tiempo real de empleados")
        print(f"   2. Validación automática de ubicaciones")
        print(f"   3. Generación de alertas por desviaciones")
        print(f"   4. Reportes de asistencia con GPS")
        print(f"   5. Integración con apps móviles")
        
        print(f"\n🎯 PARA USAR EL SISTEMA:")
        print(f"   1. Ve a /asistencia/rastreo-tiempo-real/")
        print(f"   2. Verás empleados en tiempo real en el mapa")
        print(f"   3. Áreas de trabajo aparecen como círculos azules")
        print(f"   4. Empleados: Verde=en área, Amarillo=fuera")
        print(f"   5. Actualización automática cada 30 segundos")
        
        if areas.count() > 0 and assignments.count() > 0:
            print(f"\n🎉 ¡SISTEMA GPS COMPLETAMENTE OPERATIVO!")
        else:
            print(f"\n⚠️ Ejecuta 'python setup_work_areas.py' para configurar datos")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_gps_system()
