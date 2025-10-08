"""
Comando para recalcular resúmenes de asistencia
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from attendance.models import AttendanceSummary, Attendance, Employee


class Command(BaseCommand):
    help = 'Recalcula los resúmenes de asistencia para un rango de fechas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Fecha de inicio (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='Fecha de fin (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--employee-id',
            type=int,
            help='ID del empleado (opcional, si no se especifica recalcula para todos)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Número de días hacia atrás desde hoy (por defecto: 7)',
        )

    def handle(self, *args, **options):
        # Determinar rango de fechas
        if options['start_date'] and options['end_date']:
            start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
        else:
            # Usar días hacia atrás
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=options['days'])
        
        self.stdout.write(f"\n🔄 Recalculando resúmenes de asistencia...")
        self.stdout.write(f"   Rango: {start_date} a {end_date}")
        
        # Determinar empleados
        if options['employee_id']:
            employees = Employee.objects.filter(id=options['employee_id'])
            if not employees.exists():
                self.stdout.write(self.style.ERROR(f"❌ Empleado con ID {options['employee_id']} no encontrado"))
                return
        else:
            employees = Employee.objects.filter(is_active=True)
        
        self.stdout.write(f"   Empleados: {employees.count()}")
        
        # Recalcular resúmenes
        total_updated = 0
        total_created = 0
        total_deleted = 0
        
        current_date = start_date
        while current_date <= end_date:
            for employee in employees:
                # Obtener marcaciones del día
                attendances = Attendance.objects.filter(
                    employee=employee,
                    timestamp__date=current_date
                ).order_by('timestamp')
                
                if attendances.exists():
                    # Hay marcaciones: actualizar o crear resumen
                    summary, created = AttendanceSummary.objects.get_or_create(
                        employee=employee,
                        date=current_date
                    )
                    
                    # Calcular entrada y salida
                    check_in = attendances.filter(entry_type='IN').first()
                    check_out = attendances.filter(entry_type='OUT').last()
                    
                    summary.check_in_time = check_in.timestamp.time() if check_in else None
                    summary.check_out_time = check_out.timestamp.time() if check_out else None
                    summary.is_present = True
                    
                    # Calcular tardanza (simplificado)
                    if check_in:
                        expected_time = timezone.datetime.combine(current_date, timezone.datetime.strptime('08:30', '%H:%M').time())
                        summary.is_late = check_in.timestamp.time() > expected_time.time()
                    
                    summary.save()
                    
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1
                else:
                    # No hay marcaciones: eliminar resumen si existe
                    deleted_count, _ = AttendanceSummary.objects.filter(
                        employee=employee,
                        date=current_date
                    ).delete()
                    total_deleted += deleted_count
            
            current_date += timedelta(days=1)
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Recalculación completada:"))
        self.stdout.write(f"   - Resúmenes creados: {total_created}")
        self.stdout.write(f"   - Resúmenes actualizados: {total_updated}")
        self.stdout.write(f"   - Resúmenes eliminados: {total_deleted}")
