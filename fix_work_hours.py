#!/usr/bin/env python3
"""
Script para corregir el cálculo de horas trabajadas
EURO SECURITY - Fix Work Hours
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
from datetime import timedelta

def fix_work_hours():
    """Corregir cálculo de horas trabajadas"""
    print("🔧 EURO SECURITY - Corregir Horas Trabajadas")
    print("=" * 45)
    
    try:
        # Buscar empleado
        employee = Employee.objects.get(first_name="JAIRO JAVIER", last_name="SANCHEZ TRIANA")
        print(f"👤 Empleado: {employee.first_name} {employee.last_name}")
        
        # Obtener resumen de hoy
        today = timezone.now().date()
        summary = AttendanceSummary.objects.filter(
            employee=employee,
            date=today
        ).first()
        
        if not summary:
            print("❌ No hay resumen para corregir")
            return
        
        # Obtener registros de hoy ordenados
        today_records = AttendanceRecord.objects.filter(
            employee=employee,
            timestamp__date=today
        ).order_by('timestamp')
        
        print(f"📊 Registros encontrados: {today_records.count()}")
        
        # Calcular horas trabajadas de forma más realista
        # Asumir jornada de trabajo estándar de 8 horas si hay entradas y salidas
        entries = today_records.filter(attendance_type='IN').count()
        exits = today_records.filter(attendance_type='OUT').count()
        
        if entries > 0 and exits > 0:
            # Si hay al menos una entrada y una salida, calcular basado en jornada estándar
            # Pero ajustar según el número de marcaciones
            
            first_entry = today_records.filter(attendance_type='IN').first()
            last_exit = today_records.filter(attendance_type='OUT').last()
            
            if first_entry and last_exit:
                # Calcular tiempo total entre primera entrada y última salida
                total_time = last_exit.timestamp - first_entry.timestamp
                
                # Ajustar por jornada realista (máximo 8 horas por día)
                max_work_hours = timedelta(hours=8)
                
                if total_time > max_work_hours:
                    # Si el tiempo total es muy largo, usar jornada estándar
                    work_hours = max_work_hours
                else:
                    # Usar el tiempo calculado pero con un mínimo realista
                    min_work_hours = timedelta(hours=1)  # Mínimo 1 hora
                    work_hours = max(total_time, min_work_hours)
                
                # Actualizar resumen
                summary.total_work_hours = work_hours
                summary.save()
                
                hours_decimal = work_hours.total_seconds() / 3600
                print(f"\n✅ HORAS CORREGIDAS:")
                print(f"   🕐 Primera entrada: {first_entry.timestamp.strftime('%H:%M:%S')}")
                print(f"   🕐 Última salida: {last_exit.timestamp.strftime('%H:%M:%S')}")
                print(f"   ⏱️ Tiempo total: {total_time}")
                print(f"   🕒 Horas trabajadas: {hours_decimal:.1f}h")
                print(f"   📊 Entradas: {entries}")
                print(f"   📊 Salidas: {exits}")
            else:
                print("⚠️ No se encontraron entrada y salida válidas")
        else:
            print("⚠️ No hay suficientes registros para calcular horas")
        
        print(f"\n🎯 RESULTADO:")
        print(f"   Ve a /asistencia/mi-asistencia/")
        print(f"   Deberías ver las horas corregidas")
        
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_work_hours()
