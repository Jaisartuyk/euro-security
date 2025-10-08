"""
Configuración del admin para el sistema de asistencia
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import AttendanceRecord, AttendanceSummary, FacialRecognitionProfile, AttendanceSettings
from .models import LeaveRequest, LeaveType, LeaveStatus
from .models_gps import GPSTracking, WorkArea, EmployeeWorkArea, LocationAlert

# Importar admins de seguridad con IA
from .admin_security import SecurityPhotoAdmin, SecurityAlertAdmin, VideoSessionAdmin


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'attendance_type', 'timestamp', 'verification_method', 
                   'location_display', 'facial_confidence', 'is_valid']
    list_filter = ['attendance_type', 'verification_method', 'is_valid', 'timestamp']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at', 'location_display']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('employee', 'attendance_type', 'timestamp', 'verification_method')
        }),
        ('Geolocalización', {
            'fields': ('latitude', 'longitude', 'location_accuracy', 'address'),
            'classes': ('collapse',)
        }),
        ('Datos Biométricos', {
            'fields': ('facial_confidence', 'facial_image_path'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('device_info', 'ip_address', 'notes'),
            'classes': ('collapse',)
        }),
        ('Validación', {
            'fields': ('is_valid', 'validated_by', 'validation_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def location_display(self, obj):
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">{}, {}</a>',
                obj.latitude, obj.longitude, obj.latitude, obj.longitude
            )
        return "Sin ubicación"
    location_display.short_description = "Ubicación"
    
    actions = ['mark_as_valid', 'mark_as_invalid']
    
    def mark_as_valid(self, request, queryset):
        queryset.update(is_valid=True, validated_by=request.user)
        self.message_user(request, f"{queryset.count()} registros marcados como válidos.")
    mark_as_valid.short_description = "Marcar como válidos"
    
    def mark_as_invalid(self, request, queryset):
        queryset.update(is_valid=False, validated_by=request.user)
        self.message_user(request, f"{queryset.count()} registros marcados como inválidos.")
    mark_as_invalid.short_description = "Marcar como inválidos"


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'first_entry', 'last_exit', 'work_hours_display', 
                   'is_present', 'is_late', 'is_early_exit']
    list_filter = ['date', 'is_present', 'is_late', 'is_early_exit']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['work_hours_display', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    actions = ['recalculate_summaries']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('employee', 'date')
        }),
        ('Horarios', {
            'fields': ('first_entry', 'last_exit', 'total_work_hours', 'total_break_time')
        }),
        ('Estadísticas', {
            'fields': ('entries_count', 'exits_count', 'break_count')
        }),
        ('Estado', {
            'fields': ('is_present', 'is_late', 'is_early_exit')
        }),
        ('Ubicaciones', {
            'fields': ('locations_visited',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def work_hours_display(self, obj):
        return obj.get_work_hours_display()
    work_hours_display.short_description = "Horas Trabajadas"
    
    def recalculate_summaries(self, request, queryset):
        """Recalcular resúmenes de asistencia basándose en las marcaciones actuales"""
        from datetime import datetime, timedelta
        from django.contrib import messages
        
        # Obtener empleados y fechas únicas de los resúmenes seleccionados
        employees = set(queryset.values_list('employee', flat=True))
        dates = set(queryset.values_list('date', flat=True))
        
        if not employees or not dates:
            self.message_user(request, "No hay resúmenes seleccionados", level=messages.WARNING)
            return
        
        total_updated = 0
        total_created = 0
        total_deleted = 0
        
        # Recalcular para cada combinación de empleado y fecha
        for employee_id in employees:
            employee = Employee.objects.get(id=employee_id)
            for date in dates:
                # Obtener marcaciones del día
                attendances = Attendance.objects.filter(
                    employee=employee,
                    timestamp__date=date
                ).order_by('timestamp')
                
                if attendances.exists():
                    # Hay marcaciones: actualizar o crear resumen
                    summary, created = AttendanceSummary.objects.get_or_create(
                        employee=employee,
                        date=date
                    )
                    
                    # Calcular entrada y salida
                    check_in = attendances.filter(entry_type='IN').first()
                    check_out = attendances.filter(entry_type='OUT').last()
                    
                    summary.first_entry = check_in.timestamp if check_in else None
                    summary.last_exit = check_out.timestamp if check_out else None
                    summary.is_present = True
                    
                    # Calcular tardanza (simplificado - asume horario de 08:30)
                    if check_in:
                        from django.utils import timezone
                        expected_time = timezone.datetime.combine(date, timezone.datetime.strptime('08:30', '%H:%M').time())
                        expected_time = timezone.make_aware(expected_time)
                        summary.is_late = check_in.timestamp > expected_time
                    
                    # Contar entradas y salidas
                    summary.entries_count = attendances.filter(entry_type='IN').count()
                    summary.exits_count = attendances.filter(entry_type='OUT').count()
                    
                    summary.save()
                    
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1
                else:
                    # No hay marcaciones: eliminar resumen si existe
                    deleted_count, _ = AttendanceSummary.objects.filter(
                        employee=employee,
                        date=date
                    ).delete()
                    total_deleted += deleted_count
        
        # Mensaje de éxito
        message = f"✅ Recalculación completada: {total_created} creados, {total_updated} actualizados, {total_deleted} eliminados"
        self.message_user(request, message, level=messages.SUCCESS)
    
    recalculate_summaries.short_description = "🔄 Recalcular resúmenes seleccionados"


@admin.register(FacialRecognitionProfile)
class FacialRecognitionProfileAdmin(admin.ModelAdmin):
    list_display = ['employee', 'confidence_threshold', 'success_rate_display', 
                   'total_recognitions', 'is_active', 'needs_retraining']
    list_filter = ['is_active', 'needs_retraining', 'last_recognition']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['success_rate_display', 'face_encoding', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Empleado', {
            'fields': ('employee',)
        }),
        ('Configuración', {
            'fields': ('confidence_threshold', 'is_active', 'needs_retraining')
        }),
        ('Imágenes de Referencia', {
            'fields': ('image_1', 'image_2', 'image_3', 'image_4', 'image_5'),
            'description': '📷 Sube 2-5 imágenes del empleado. El sistema procesará automáticamente las características faciales.'
        }),
        ('Datos del Modelo (Solo Lectura)', {
            'fields': ('face_encoding', 'reference_images'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('total_recognitions', 'successful_recognitions', 'success_rate_display', 'last_recognition')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def success_rate_display(self, obj):
        if obj.total_recognitions > 0:
            rate = (obj.successful_recognitions / obj.total_recognitions) * 100
            color = 'green' if rate >= 90 else 'orange' if rate >= 70 else 'red'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, f"{rate:.1f}%"
            )
        return '-'
    success_rate_display.short_description = "Tasa de Éxito"
    

    
    actions = ['reset_statistics', 'mark_for_retraining', 'process_images']
    
    def save_model(self, request, obj, form, change):
        """Procesa automáticamente las imágenes al guardar"""
        super().save_model(request, obj, form, change)
        
        # Si hay imágenes subidas, procesarlas automáticamente
        images = [obj.image_1, obj.image_2, obj.image_3, obj.image_4, obj.image_5]
        if any(img and img.name for img in images):
            success, message = obj.process_uploaded_images()
            if success:
                self.message_user(request, f"✅ {message}", level='SUCCESS')
            else:
                self.message_user(request, f"⚠️ {message}", level='WARNING')
    
    def reset_statistics(self, request, queryset):
        for profile in queryset:
            profile.total_recognitions = 0
            profile.successful_recognitions = 0
            profile.save()
        self.message_user(request, f"Estadísticas reiniciadas para {queryset.count()} perfiles.")
    reset_statistics.short_description = "Reiniciar estadísticas"
    
    def mark_for_retraining(self, request, queryset):
        queryset.update(needs_retraining=True)
        self.message_user(request, f"{queryset.count()} perfiles marcados para reentrenamiento.")
    mark_for_retraining.short_description = "Marcar para reentrenamiento"
    
    def process_images(self, request, queryset):
        """Procesa las imágenes de los perfiles seleccionados"""
        processed = 0
        for profile in queryset:
            success, message = profile.process_uploaded_images()
            if success:
                processed += 1
        
        if processed > 0:
            self.message_user(request, f"✅ {processed} perfiles procesados exitosamente.")
        else:
            self.message_user(request, "⚠️ No se pudieron procesar los perfiles seleccionados.", level='WARNING')
    process_images.short_description = "Procesar imágenes"


@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    list_display = ['work_start_time', 'work_end_time', 'late_tolerance_minutes', 
                   'facial_confidence_threshold', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Horarios de Trabajo', {
            'fields': ('work_start_time', 'work_end_time', 'break_duration_minutes')
        }),
        ('Tolerancias', {
            'fields': ('late_tolerance_minutes', 'early_exit_tolerance_minutes', 'location_tolerance_meters')
        }),
        ('Reconocimiento Facial', {
            'fields': ('facial_confidence_threshold', 'max_recognition_attempts')
        }),
        ('Ubicaciones de Trabajo', {
            'fields': ('work_locations',),
            'description': 'JSON con las ubicaciones de trabajo permitidas'
        }),
        ('Control', {
            'fields': ('is_active', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ============================================================================
# MODELOS GPS
# ============================================================================

@admin.register(GPSTracking)
class GPSTrackingAdmin(admin.ModelAdmin):
    list_display = ('employee', 'timestamp', 'latitude', 'longitude', 'accuracy', 
                   'is_within_work_area', 'work_area', 'tracking_type')
    list_filter = ('tracking_type', 'is_within_work_area', 'timestamp', 'work_area')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id')
    readonly_fields = ('timestamp', 'distance_to_work_area', 'created_at', 'updated_at')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Empleado', {
            'fields': ('employee',)
        }),
        ('Ubicación GPS', {
            'fields': ('latitude', 'longitude', 'accuracy', 'altitude')
        }),
        ('Información de Rastreo', {
            'fields': ('tracking_type', 'is_active_session')
        }),
        ('Área de Trabajo', {
            'fields': ('work_area', 'is_within_work_area', 'distance_to_work_area')
        }),
        ('Dispositivo', {
            'fields': ('battery_level', 'device_info', 'notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'work_area')


@admin.register(WorkArea)
class WorkAreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'area_type', 'latitude', 'longitude', 'radius_meters', 
                   'is_active', 'requires_attendance')
    list_filter = ('area_type', 'is_active', 'requires_attendance')
    search_fields = ('name', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'area_type')
        }),
        ('Ubicación GPS', {
            'fields': ('latitude', 'longitude', 'radius_meters', 'address')
        }),
        ('Contacto', {
            'fields': ('contact_person', 'contact_phone')
        }),
        ('Horarios', {
            'fields': ('start_time', 'end_time')
        }),
        ('Configuración', {
            'fields': ('requires_attendance', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(EmployeeWorkArea)
class EmployeeWorkAreaAdmin(admin.ModelAdmin):
    list_display = ('employee', 'work_area', 'is_primary', 'assigned_date', 'is_active')
    list_filter = ('is_primary', 'is_active', 'assigned_date', 'work_area')
    search_fields = ('employee__first_name', 'employee__last_name', 'work_area__name')
    readonly_fields = ('assigned_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Asignación', {
            'fields': ('employee', 'work_area', 'is_primary', 'is_active')
        }),
        ('Fechas', {
            'fields': ('assigned_date', 'start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'work_area')


@admin.register(LocationAlert)
class LocationAlertAdmin(admin.ModelAdmin):
    list_display = ('employee', 'alert_type', 'alert_level', 'title', 'is_resolved', 'created_at')
    list_filter = ('alert_type', 'alert_level', 'is_resolved', 'created_at')
    search_fields = ('employee__first_name', 'employee__last_name', 'title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Alerta', {
            'fields': ('employee', 'work_area', 'gps_tracking')
        }),
        ('Detalles', {
            'fields': ('alert_type', 'alert_level', 'title', 'message')
        }),
        ('Estado', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee', 'work_area', 'gps_tracking')


# ============================================================================
# SISTEMA DE AUSENCIAS Y PERMISOS LABORALES
# ============================================================================

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """Admin para solicitudes de ausencia laboral"""
    
    list_display = ('request_number', 'employee', 'leave_type', 'status_badge', 
                   'permission_mode', 'total_days_hours', 'submitted_at', 'ai_badge')
    list_filter = ('status', 'leave_type', 'permission_mode', 'ai_generated', 
                  'submitted_at', 'created_at')
    search_fields = ('request_number', 'employee__first_name', 'employee__last_name',
                    'employee__employee_id', 'reason_description')
    readonly_fields = ('request_number', 'created_at', 'updated_at', 'employee_code',
                      'ai_generated', 'ai_confidence', 'submitted_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('📋 Datos de la Solicitud', {
            'fields': ('request_number', 'status', 'submitted_at')
        }),
        ('👤 Empleado Solicitante', {
            'fields': ('employee', 'employee_code', 'project', 'area', 'immediate_supervisor')
        }),
        ('📝 Tipo de Permiso', {
            'fields': ('leave_type', 'permission_mode', 'reason_description')
        }),
        ('📅 Duración - Por Días', {
            'fields': ('start_date', 'end_date', 'total_days'),
            'classes': ('collapse',)
        }),
        ('⏰ Duración - Por Horas', {
            'fields': ('permission_date', 'start_time', 'end_time', 'total_hours'),
            'classes': ('collapse',)
        }),
        ('📄 Documentación', {
            'fields': ('supporting_document',)
        }),
        ('🤖 Integración Dr. Claude IA', {
            'fields': ('medical_leave', 'ai_generated', 'ai_confidence', 'ai_recommendation'),
            'classes': ('collapse',)
        }),
        ('✅ Aprobación Jefe Inmediato', {
            'fields': ('supervisor_reviewed_by', 'supervisor_comments', 
                      'supervisor_decision_date', 'supervisor_signature_date')
        }),
        ('✅ Aprobación RRHH', {
            'fields': ('hr_reviewed_by', 'hr_comments', 
                      'hr_decision_date', 'hr_signature_date')
        }),
        ('🔄 Impacto en Turnos', {
            'fields': ('affects_shifts', 'shifts_affected', 'requires_coverage', 'replacement_employee'),
            'classes': ('collapse',)
        }),
        ('🕐 Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Badge de estado con colores"""
        color = obj.get_status_color()
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def ai_badge(self, obj):
        """Badge si fue generado por IA"""
        if obj.ai_generated:
            return format_html(
                '<span class="badge bg-info" title="Confianza: {:.0%}">🤖 IA</span>',
                obj.ai_confidence
            )
        return '-'
    ai_badge.short_description = 'IA'
    
    def total_days_hours(self, obj):
        """Muestra días u horas según el modo"""
        if obj.permission_mode == 'DAYS':
            return f"{obj.total_days} días"
        else:
            return f"{obj.total_hours} horas"
    total_days_hours.short_description = 'Duración'
    
    actions = ['approve_by_supervisor_action', 'approve_by_hr_action', 'reject_action']
    
    def approve_by_supervisor_action(self, request, queryset):
        """Aprobar solicitudes como jefe"""
        count = 0
        for leave in queryset:
            if leave.status == LeaveStatus.PENDING_SUPERVISOR:
                leave.approve_by_supervisor(request.user, "Aprobado desde admin")
                count += 1
        self.message_user(request, f"{count} solicitudes aprobadas por jefe.")
    approve_by_supervisor_action.short_description = "✅ Aprobar como Jefe"
    
    def approve_by_hr_action(self, request, queryset):
        """Aprobar solicitudes como RRHH"""
        count = 0
        for leave in queryset:
            if leave.status == LeaveStatus.PENDING_HR:
                leave.approve_by_hr(request.user, "Aprobado desde admin")
                count += 1
        self.message_user(request, f"{count} solicitudes aprobadas por RRHH.")
    approve_by_hr_action.short_description = "✅ Aprobar como RRHH"
    
    def reject_action(self, request, queryset):
        """Rechazar solicitudes"""
        count = 0
        for leave in queryset:
            if leave.status in [LeaveStatus.PENDING_SUPERVISOR, LeaveStatus.PENDING_HR]:
                if leave.status == LeaveStatus.PENDING_SUPERVISOR:
                    leave.reject_by_supervisor(request.user, "Rechazado desde admin")
                else:
                    leave.reject_by_hr(request.user, "Rechazado desde admin")
                count += 1
        self.message_user(request, f"{count} solicitudes rechazadas.")
    reject_action.short_description = "❌ Rechazar"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'employee', 'area', 'immediate_supervisor',
            'supervisor_reviewed_by', 'hr_reviewed_by',
            'medical_leave', 'replacement_employee'
        )
