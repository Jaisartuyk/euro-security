#!/usr/bin/env python3
"""
Script simplificado para regenerar resúmenes diarios de asistencia
EURO SECURITY - Fix Summaries Simple
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models import AttendanceRecord, AttendanceSummary, AttendanceSettings
from employees.models import Employee
from django.utils import timezone
from datetime import datetime, timedelta

def update_daily_summary_simple(employee, attendance_record):
    """Versión simplificada de update_daily_summary"""
    date = attendance_record.timestamp.date()
    
    summary, created = AttendanceSummary.objects.get_or_create(
        employee=employee,
        date=date,
        defaults={
            'first_entry': None,
            'last_exit': None,
            'entries_count': 0,
            'exits_count': 0,
            'break_count': 0,
            'is_present': False,
            'is_late': False,
            'is_early_exit': False,
        }
    )
    
    # Actualizar contadores
    if attendance_record.attendance_type == 'IN':
        summary.entries_count += 1
        if not summary.first_entry:
            summary.first_entry = attendance_record.timestamp
            summary.is_present = True
            
            # Verificar si llegó tarde (simplificado)
            work_start_hour = 8  # 8:00 AM
            if attendance_record.timestamp.hour > work_start_hour:
                summary.is_late = True
    
    elif attendance_record.attendance_type == 'OUT':
        summary.exits_count += 1
        summary.last_exit = attendance_record.timestamp
        
        # Verificar salida temprana (simplificado)
        work_end_hour = 17  # 5:00 PM
        if attendance_record.timestamp.hour < work_end_hour:
            summary.is_early_exit = True
    
    elif attendance_record.attendance_type in ['BREAK_OUT', 'BREAK_IN']:
        summary.break_count += 1
    
    # Calcular horas trabajadas
    if summary.first_entry and summary.last_exit:
        summary.total_work_hours = summary.last_exit - summary.first_entry
    
    summary.save()
    return summary

def regenerate_summaries():
    """Regenerar resúmenes diarios para registros existentes"""
    print("🔄 EURO SECURITY - Regenerar Resúmenes Diarios (Versión Simple)")
    print("=" * 60)
    
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
        AttendanceSummary.objects.filter(
            employee=employee,
            date=today
        ).delete()
        print("🗑️ Resúmenes anteriores eliminados")
        
        # Regenerar resúmenes procesando cada registro
        print("🔄 Regenerando resúmenes...")
        summary = None
        for i, record in enumerate(today_records, 1):
            summary = update_daily_summary_simple(employee, record)
            print(f"   ✅ Procesado {i}/{today_records.count()}: {record.get_attendance_type_display()} - {record.timestamp.strftime('%H:%M:%S')}")
        
        # Verificar resumen generado
        if summary:
            print(f"\n🎉 RESUMEN GENERADO EXITOSAMENTE:")
            print(f"   📅 Fecha: {summary.date}")
            print(f"   🕐 Primera entrada: {summary.first_entry.strftime('%H:%M:%S') if summary.first_entry else 'N/A'}")
            print(f"   🕐 Última salida: {summary.last_exit.strftime('%H:%M:%S') if summary.last_exit else 'N/A'}")
            print(f"   📊 Entradas: {summary.entries_count}")
            print(f"   📊 Salidas: {summary.exits_count}")
            print(f"   📊 Descansos: {summary.break_count}")
            print(f"   ✅ Presente: {'Sí' if summary.is_present else 'No'}")
            print(f"   ⏰ Tarde: {'Sí' if summary.is_late else 'No'}")
            print(f"   🚪 Salida temprana: {'Sí' if summary.is_early_exit else 'No'}")
            if summary.total_work_hours:
                hours = summary.total_work_hours.total_seconds() / 3600
                print(f"   🕒 Horas trabajadas: {hours:.1f}h")
            else:
                print(f"   🕒 Horas trabajadas: Calculando...")
        else:
            print("❌ No se pudo generar el resumen")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"   1. Ve a /asistencia/mi-asistencia/")
        print(f"   2. Deberías ver:")
        print(f"      - Días Presente: 1")
        print(f"      - Días Tarde: {'1' if summary and summary.is_late else '0'}")
        print(f"      - Días Laborales: 1")
        print(f"      - Promedio Horas: {hours:.1f}h" if summary and summary.total_work_hours else "Calculando...")
        print(f"   3. El dashboard debería mostrar los datos correctos")
        
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    regenerate_summaries()
