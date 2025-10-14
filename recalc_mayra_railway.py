"""
Script para recalcular resúmenes de Mayra en Railway
Ejecutar: railway run python recalc_mayra_railway.py
"""
import os, sys, django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.utils import timezone
from employees.models import Employee
from attendance.models import AttendanceRecord, AttendanceSummary

print("\n" + "="*70)
print("RECALCULAR RESUMENES - MAYRA ALEJANDRA ESPINOZA PONCE")
print("="*70 + "\n")

# Buscar a Mayra
employee_id = 'EMP13807414'

try:
    employee = Employee.objects.get(employee_id=employee_id)
    print(f"✅ Empleado encontrado: {employee.get_full_name()}")
    print(f"📋 ID: {employee.employee_id}")
    print(f"📧 Email: {employee.email}")
except Employee.DoesNotExist:
    print(f"❌ ERROR: No se encontro empleado con ID: {employee_id}")
    print("\n🔍 Listando primeros 10 empleados en la BD:")
    for emp in Employee.objects.all()[:10]:
        print(f"   - {emp.get_full_name()} ({emp.employee_id})")
    sys.exit(1)

# Fechas
start_date = datetime(2025, 10, 1).date()
end_date = datetime(2025, 10, 14).date()

print(f"\n📅 Rango: {start_date} hasta {end_date}")
print("-" * 70)

# Recalcular
current_date = start_date
total_days = 0
days_with_data = 0

while current_date <= end_date:
    records = AttendanceRecord.objects.filter(
        employee=employee,
        timestamp__date=current_date
    ).order_by('timestamp')
    
    if records.exists():
        days_with_data += 1
        
        # Eliminar resumen antiguo
        deleted = AttendanceSummary.objects.filter(
            employee=employee,
            date=current_date
        ).delete()
        
        if deleted[0] > 0:
            print(f"🗑️  {current_date}: Eliminado resumen antiguo")
        
        # Crear nuevo resumen
        summary = AttendanceSummary(
            employee=employee,
            date=current_date,
            first_entry=None,
            last_exit=None,
            entries_count=0,
            exits_count=0,
            break_count=0,
            is_present=False,
            is_late=False,
            is_early_exit=False
        )
        
        # Procesar cada registro
        for record in records:
            if record.attendance_type == 'IN':
                summary.entries_count += 1
                if not summary.first_entry:
                    summary.first_entry = record.timestamp
                    summary.is_present = True
                    local_time = record.timestamp.astimezone()
                    if local_time.hour > 8 or (local_time.hour == 8 and local_time.minute > 15):
                        summary.is_late = True
            
            elif record.attendance_type == 'OUT':
                summary.exits_count += 1
                summary.last_exit = record.timestamp
                local_time = record.timestamp.astimezone()
                if local_time.hour < 17:
                    summary.is_early_exit = True
            
            elif record.attendance_type in ['BREAK_OUT', 'BREAK_IN']:
                summary.break_count += 1
        
        # Calcular horas trabajadas
        if summary.first_entry and summary.last_exit:
            work_duration = summary.last_exit - summary.first_entry
            summary.total_work_hours = min(work_duration, timedelta(hours=24))
        
        summary.save()
        
        # Mostrar resultado
        hours = str(summary.total_work_hours) if summary.total_work_hours else "0:00:00"
        print(f"✅ {current_date}: Entradas={summary.entries_count}, Salidas={summary.exits_count}, Horas={hours}")
        
        # Mostrar detalles de registros
        for rec in records:
            lt = rec.timestamp.astimezone()
            print(f"   📍 {rec.attendance_type}: {lt.strftime('%H:%M:%S')}")
    
    total_days += 1
    current_date += timedelta(days=1)

print("-" * 70)
print(f"\n✨ COMPLETADO:")
print(f"   📊 Dias procesados: {total_days}")
print(f"   📈 Dias con registros: {days_with_data}")
print(f"   ✅ Resumenes actualizados correctamente")
print("\n" + "="*70 + "\n")
