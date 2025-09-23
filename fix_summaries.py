#!/usr/bin/env python3
"""
Script para regenerar resúmenes diarios de asistencia
EURO SECURITY - Fix Summaries
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models import AttendanceRecord, AttendanceSummary
from employees.models import Employee
from django.utils import timezone
from attendance.views import update_daily_summary

def regenerate_summaries():
    """Regenerar resúmenes diarios para registros existentes"""
    print("🔄 EURO SECURITY - Regenerar Resúmenes Diarios")
    print("=" * 50)
    
    try:
        # Buscar empleado
        employee = Employee.objects.get(first_name="JAIRO JAVIER", last_name="SANCHEZ TRIANA")
        print(f"👤 Empleado: {employee.first_name} {employee.last_name}")
        
        # Obtener registros de hoy
        today = timezone.now().date()
        today_records = AttendanceRecord.objects.filter(
            employee=employee,
            timestamp__date=today
        ).order_by('timestamp')
        
        print(f"📊 Registros encontrados para {today}: {today_records.count()}")
        
        # Eliminar resumen existente si existe
        existing_summary = AttendanceSummary.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if existing_summary:
            existing_summary.delete()
            print("🗑️ Resumen anterior eliminado")
        
        # Regenerar resúmenes procesando cada registro
        print("🔄 Regenerando resúmenes...")
        for i, record in enumerate(today_records, 1):
            update_daily_summary(employee, record)
            print(f"   Procesado {i}/{today_records.count()}: {record.get_attendance_type_display()} - {record.timestamp.strftime('%H:%M:%S')}")
        
        # Verificar resumen generado
        new_summary = AttendanceSummary.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if new_summary:
            print(f"\n✅ RESUMEN GENERADO EXITOSAMENTE:")
            print(f"   📅 Fecha: {new_summary.date}")
            print(f"   🕐 Primera entrada: {new_summary.first_entry.strftime('%H:%M:%S') if new_summary.first_entry else 'N/A'}")
            print(f"   🕐 Última salida: {new_summary.last_exit.strftime('%H:%M:%S') if new_summary.last_exit else 'N/A'}")
            print(f"   📊 Entradas: {new_summary.entries_count}")
            print(f"   📊 Salidas: {new_summary.exits_count}")
            print(f"   ✅ Presente: {'Sí' if new_summary.is_present else 'No'}")
            print(f"   ⏰ Tarde: {'Sí' if new_summary.is_late else 'No'}")
            print(f"   🕒 Horas trabajadas: {new_summary.get_work_hours_display()}")
        else:
            print("❌ No se pudo generar el resumen")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"   1. Ve a /asistencia/mi-asistencia/")
        print(f"   2. Deberías ver las estadísticas actualizadas")
        print(f"   3. El dashboard debería mostrar los datos correctos")
        
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    regenerate_summaries()
