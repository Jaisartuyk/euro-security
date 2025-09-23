"""
Configuración del admin para el sistema de asistencia
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import AttendanceRecord, AttendanceSummary, FacialRecognitionProfile, AttendanceSettings


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
