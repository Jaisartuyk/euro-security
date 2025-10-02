"""
Management command para corregir horas de asistencia en registros antiguos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import AttendanceSummary, AttendanceRecord
from datetime import datetime, time as dt_time


class Command(BaseCommand):
    help = 'Corrige las horas de first_entry y last_exit en registros antiguos de AttendanceSummary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula la corrección sin guardar cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: No se guardarán cambios'))
        
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando corrección de horas de asistencia...'))
        
        # Obtener todos los resúmenes
        summaries = AttendanceSummary.objects.all().order_by('date')
        total = summaries.count()
        
        self.stdout.write(f'📊 Total de registros a revisar: {total}')
        
        corrected = 0
        skipped = 0
        errors = 0
        
        for summary in summaries:
            try:
                needs_correction = False
                
                # Verificar si first_entry necesita corrección
                if summary.first_entry:
                    # Si first_entry es medianoche (00:00), probablemente está mal
                    if summary.first_entry.hour == 0 and summary.first_entry.minute < 30:
                        needs_correction = True
                
                # Verificar si last_exit necesita corrección
                if summary.last_exit:
                    # Si last_exit es medianoche (00:00), probablemente está mal
                    if summary.last_exit.hour == 0 and summary.last_exit.minute < 30:
                        needs_correction = True
                
                if needs_correction:
                    # Buscar registros reales de ese día
                    records = AttendanceRecord.objects.filter(
                        employee=summary.employee,
                        timestamp__date=summary.date
                    ).order_by('timestamp')
                    
                    if records.exists():
                        # Encontrar primera entrada
                        first_in = records.filter(attendance_type='IN').first()
                        if first_in:
                            old_first = summary.first_entry
                            summary.first_entry = first_in.timestamp.time()
                            self.stdout.write(
                                f'  ✓ {summary.employee.get_full_name()} - {summary.date}: '
                                f'Primera entrada {old_first} → {summary.first_entry}'
                            )
                        
                        # Encontrar última salida
                        last_out = records.filter(attendance_type='OUT').last()
                        if last_out:
                            old_last = summary.last_exit
                            summary.last_exit = last_out.timestamp.time()
                            self.stdout.write(
                                f'  ✓ {summary.employee.get_full_name()} - {summary.date}: '
                                f'Última salida {old_last} → {summary.last_exit}'
                            )
                        
                        # Recalcular horas trabajadas
                        if summary.first_entry and summary.last_exit:
                            from datetime import timedelta
                            first_entry_dt = datetime.combine(summary.date, summary.first_entry)
                            last_exit_dt = datetime.combine(summary.date, summary.last_exit)
                            
                            work_duration = last_exit_dt - first_entry_dt
                            max_hours = timedelta(hours=8)
                            summary.total_work_hours = min(work_duration, max_hours)
                        
                        if not dry_run:
                            summary.save()
                        
                        corrected += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠️  No se encontraron registros para {summary.employee.get_full_name()} - {summary.date}'
                            )
                        )
                        skipped += 1
                else:
                    skipped += 1
                    
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'  ❌ Error en {summary.employee.get_full_name()} - {summary.date}: {str(e)}'
                    )
                )
        
        # Resumen final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✨ RESUMEN DE CORRECCIÓN:'))
        self.stdout.write(f'📊 Total revisados: {total}')
        self.stdout.write(self.style.SUCCESS(f'✅ Corregidos: {corrected}'))
        self.stdout.write(self.style.WARNING(f'⏭️  Omitidos (correctos): {skipped}'))
        if errors > 0:
            self.stdout.write(self.style.ERROR(f'❌ Errores: {errors}'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  MODO DRY-RUN: No se guardaron cambios'))
            self.stdout.write('Para aplicar los cambios, ejecuta sin --dry-run')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Cambios guardados exitosamente'))
