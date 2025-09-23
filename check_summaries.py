#!/usr/bin/env python3
"""
Script para verificar resúmenes diarios generados
EURO SECURITY - Check Summaries
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

def check_summaries():
    """Verificar resúmenes diarios"""
    print("📊 EURO SECURITY - Verificar Resúmenes")
    print("=" * 40)
    
    try:
        # Buscar empleado
        employee = Employee.objects.get(first_name="JAIRO JAVIER", last_name="SANCHEZ TRIANA")
        print(f"👤 Empleado: {employee.first_name} {employee.last_name}")
        
        # Verificar registros de hoy
        today = timezone.now().date()
        today_records = AttendanceRecord.objects.filter(
            employee=employee,
            timestamp__date=today
        ).count()
        
        print(f"📊 Registros de hoy: {today_records}")
        
        # Verificar resúmenes
        summaries = AttendanceSummary.objects.filter(
            employee=employee,
            date=today
        )
        
        print(f"📋 Resúmenes encontrados: {summaries.count()}")
        
        if summaries.exists():
            summary = summaries.first()
            print(f"\n✅ RESUMEN ACTUAL:")
            print(f"   📅 Fecha: {summary.date}")
            print(f"   ✅ Presente: {'Sí' if summary.is_present else 'No'}")
            print(f"   📊 Entradas: {summary.entries_count}")
            print(f"   📊 Salidas: {summary.exits_count}")
            print(f"   ⏰ Tarde: {'Sí' if summary.is_late else 'No'}")
            
            if summary.total_work_hours:
                hours = summary.total_work_hours.total_seconds() / 3600
                print(f"   🕒 Horas: {hours:.1f}h")
            else:
                print(f"   🕒 Horas: No calculadas")
        else:
            print("❌ No hay resúmenes generados")
            
        # Verificar estadísticas del mes
        start_of_month = today.replace(day=1)
        monthly_summaries = AttendanceSummary.objects.filter(
            employee=employee,
            date__range=[start_of_month, today]
        )
        
        print(f"\n📈 ESTADÍSTICAS DEL MES:")
        print(f"   📊 Total días con registros: {monthly_summaries.count()}")
        print(f"   ✅ Días presente: {monthly_summaries.filter(is_present=True).count()}")
        print(f"   ⏰ Días tarde: {monthly_summaries.filter(is_late=True).count()}")
        
        if monthly_summaries.exists():
            total_hours = sum([
                s.total_work_hours.total_seconds() / 3600 
                for s in monthly_summaries 
                if s.total_work_hours
            ])
            avg_hours = total_hours / monthly_summaries.count() if monthly_summaries.count() > 0 else 0
            print(f"   🕒 Promedio horas: {avg_hours:.1f}h")
        
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_summaries()
