"""
Comando para recalcular resúmenes de asistencia de empleados específicos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from attendance.models import AttendanceRecord, AttendanceSummary
from employees.models import Employee


class Command(BaseCommand):
    help = 'Recalcula los resúmenes de asistencia para empleados específicos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--employee-code',
            type=str,
            help='Código del empleado (ej: EMP13807414)',
        )
        parser.add_argument(
            '--date-from',
            type=str,
            help='Fecha inicio (formato: YYYY-MM-DD)',
        )
        parser.add_argument(
            '--date-to',
            type=str,
            help='Fecha fin (formato: YYYY-MM-DD)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Recalcular todos los empleados',
        )

    def handle(self, *args, **options):
        employee_code = options.get('employee_code')
        date_from = options.get('date_from')
        date_to = options.get('date_to')
        all_employees = options.get('all')

        # Determinar rango de fechas
        if date_from:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        else:
            start_date = timezone.now().date() - timedelta(days=30)  # Últimos 30 días por defecto

        if date_to:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        else:
            end_date = timezone.now().date()

        self.stdout.write(f"\n📅 Rango de fechas: {start_date} a {end_date}\n")

        # Determinar empleados
        if all_employees:
            employees = Employee.objects.filter(is_active=True)
            self.stdout.write(f"👥 Recalculando TODOS los empleados activos ({employees.count()})\n")
        elif employee_code:
            try:
                employees = Employee.objects.filter(employee_code=employee_code)
                if not employees.exists():
                    self.stdout.write(self.style.ERROR(f'❌ No se encontró empleado con código: {employee_code}'))
                    return
                self.stdout.write(f"👤 Recalculando empleado: {employees.first().get_full_name()} ({employee_code})\n")
            except Employee.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ No se encontró empleado con código: {employee_code}'))
                return
        else:
            self.stdout.write(self.style.ERROR('❌ Debes especificar --employee-code o --all'))
            return

        # Recalcular para cada empleado
        total_summaries = 0
        total_employees = 0

        for employee in employees:
            self.stdout.write(f"\n🔄 Procesando: {employee.get_full_name()} ({employee.employee_code})")
            
            # Recorrer cada día en el rango
            current_date = start_date
            employee_summaries = 0
            
            while current_date <= end_date:
                # Obtener todos los registros del día
                day_records = AttendanceRecord.objects.filter(
                    employee=employee,
                    timestamp__date=current_date
                ).order_by('timestamp')

                if day_records.exists():
                    # Eliminar resumen existente
                    AttendanceSummary.objects.filter(
                        employee=employee,
                        date=current_date
                    ).delete()

                    # Crear nuevo resumen
                    summary = AttendanceSummary.objects.create(
                        employee=employee,
                        date=current_date,
                        first_entry=None,
                        last_exit=None,
                        entries_count=0,
                        exits_count=0,
                        break_count=0,
                        is_present=False,
                        is_late=False,
                        is_early_exit=False,
                    )

                    # Procesar cada registro
                    for record in day_records:
                        if record.attendance_type == 'IN':
                            summary.entries_count += 1
                            if not summary.first_entry:
                                summary.first_entry = record.timestamp
                                summary.is_present = True
                                
                                # Verificar si llegó tarde (después de las 8:00 AM)
                                local_time = record.timestamp.astimezone()
                                if local_time.hour > 8 or (local_time.hour == 8 and local_time.minute > 15):
                                    summary.is_late = True
                        
                        elif record.attendance_type == 'OUT':
                            summary.exits_count += 1
                            summary.last_exit = record.timestamp
                            
                            # Verificar salida temprana (antes de las 5:00 PM)
                            local_time = record.timestamp.astimezone()
                            if local_time.hour < 17:
                                summary.is_early_exit = True
                        
                        elif record.attendance_type in ['BREAK_OUT', 'BREAK_IN']:
                            summary.break_count += 1

                    # Calcular horas trabajadas
                    if summary.first_entry and summary.last_exit:
                        work_duration = summary.last_exit - summary.first_entry
                        # Limitar a máximo 24 horas por día
                        max_hours = timedelta(hours=24)
                        summary.total_work_hours = min(work_duration, max_hours)
                    
                    summary.save()
                    employee_summaries += 1
                    
                    self.stdout.write(
                        f"   ✅ {current_date}: "
                        f"Entradas={summary.entries_count}, "
                        f"Salidas={summary.exits_count}, "
                        f"Horas={summary.total_work_hours if summary.total_work_hours else '0:00:00'}"
                    )

                current_date += timedelta(days=1)

            if employee_summaries > 0:
                total_summaries += employee_summaries
                total_employees += 1
                self.stdout.write(self.style.SUCCESS(f"   ✨ Recalculados {employee_summaries} días"))

        # Resumen final
        self.stdout.write(self.style.SUCCESS(
            f"\n\n🎉 COMPLETADO:\n"
            f"   👥 Empleados procesados: {total_employees}\n"
            f"   📊 Resúmenes recalculados: {total_summaries}\n"
        ))
