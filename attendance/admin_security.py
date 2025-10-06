"""
Admin para modelos de seguridad con IA
"""
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models_security_photos import SecurityPhoto, SecurityAlert, VideoSession


@admin.register(SecurityPhoto)
class SecurityPhotoAdmin(admin.ModelAdmin):
    """Admin para fotos de seguridad con análisis IA"""
    
    list_display = ('employee', 'timestamp', 'capture_type', 'alert_badge', 
                   'ai_badge', 'location_link', 'thumbnail_preview')
    list_filter = ('capture_type', 'has_alerts', 'alert_level', 'ai_analyzed', 'timestamp')
    search_fields = ('employee__first_name', 'employee__last_name', 'employee__employee_id', 'address')
    readonly_fields = ('created_at', 'updated_at', 'ai_analysis_date', 'thumbnail_preview', 
                      'photo_preview', 'ai_results_display', 'location_map')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('📸 Información de la Foto', {
            'fields': ('employee', 'photo', 'photo_preview', 'thumbnail', 'thumbnail_preview')
        }),
        ('📍 Ubicación', {
            'fields': ('latitude', 'longitude', 'work_area', 'address', 'location_map')
        }),
        ('🎯 Captura', {
            'fields': ('capture_type', 'timestamp', 'device_info')
        }),
        ('🤖 Análisis IA', {
            'fields': ('ai_analyzed', 'ai_analysis_date', 'ai_results_display'),
            'classes': ('collapse',)
        }),
        ('🚨 Alertas', {
            'fields': ('has_alerts', 'alert_level')
        }),
        ('🕐 Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['analyze_with_ai_action', 'clear_alerts_action']
    
    def alert_badge(self, obj):
        """Badge de alerta con colores"""
        if not obj.has_alerts:
            return format_html('<span style="color: green;">✓ Sin Alertas</span>')
        
        colors = {
            'LOW': '#fbbf24',
            'MEDIUM': '#f97316',
            'HIGH': '#ef4444',
            'CRITICAL': '#dc2626'
        }
        color = colors.get(obj.alert_level, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">🚨 {}</span>',
            color, obj.get_alert_level_display()
        )
    alert_badge.short_description = 'Alertas'
    
    def ai_badge(self, obj):
        """Badge de análisis IA"""
        if obj.ai_analyzed:
            return format_html('<span style="color: green;">✓ Analizado</span>')
        return format_html('<span style="color: gray;">⏳ Pendiente</span>')
    ai_badge.short_description = 'IA'
    
    def location_link(self, obj):
        """Link a Google Maps"""
        if obj.latitude and obj.longitude:
            return format_html(
                '<a href="https://maps.google.com/?q={},{}" target="_blank">📍 Ver Mapa</a>',
                obj.latitude, obj.longitude
            )
        return '-'
    location_link.short_description = 'Ubicación'
    
    def thumbnail_preview(self, obj):
        """Preview de la miniatura"""
        if obj.thumbnail:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 5px;" />', obj.thumbnail.url)
        return '-'
    thumbnail_preview.short_description = 'Preview'
    
    def photo_preview(self, obj):
        """Preview de la foto completa"""
        if obj.photo:
            return format_html('<img src="{}" style="max-width: 600px; border-radius: 10px;" />', obj.photo.url)
        return '-'
    photo_preview.short_description = 'Foto'
    
    def ai_results_display(self, obj):
        """Muestra resultados del análisis IA"""
        if not obj.ai_results:
            return '-'
        
        html = '<div style="font-family: monospace; background: #f3f4f6; padding: 10px; border-radius: 5px;">'
        
        # Armas detectadas
        if obj.ai_results.get('weapons'):
            html += '<p style="color: #dc2626; font-weight: bold;">🔫 ARMAS DETECTADAS: {}</p>'.format(
                len(obj.ai_results['weapons'])
            )
        
        # EPP
        if obj.ai_results.get('ppe'):
            html += '<p>🦺 EPP Detectado: {} objetos</p>'.format(len(obj.ai_results['ppe']))
        
        # Vehículos
        if obj.ai_results.get('vehicles'):
            html += '<p>🚗 Vehículos: {}</p>'.format(len(obj.ai_results['vehicles']))
        
        # Personas
        if obj.ai_results.get('persons'):
            html += '<p>👤 Personas: {}</p>'.format(len(obj.ai_results['persons']))
        
        # Atributos faciales
        if obj.ai_results.get('face_attributes'):
            attrs = obj.ai_results['face_attributes']
            html += '<p>👤 Rostro: Edad ~{}, {}</p>'.format(
                attrs.get('age', 'N/A'),
                attrs.get('gender', 'N/A')
            )
        
        html += '</div>'
        return mark_safe(html)
    ai_results_display.short_description = 'Resultados IA'
    
    def location_map(self, obj):
        """Mapa embebido de la ubicación"""
        if obj.latitude and obj.longitude:
            return format_html(
                '<iframe width="600" height="400" frameborder="0" style="border:0" '
                'src="https://www.google.com/maps/embed/v1/place?key=AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ&q={},{}" '
                'allowfullscreen></iframe>',
                obj.latitude, obj.longitude
            )
        return '-'
    location_map.short_description = 'Mapa'
    
    def analyze_with_ai_action(self, request, queryset):
        """Analizar fotos seleccionadas con IA"""
        count = 0
        for photo in queryset:
            if not photo.ai_analyzed:
                photo.analyze_with_ai()
                count += 1
        
        self.message_user(request, f'✅ {count} fotos analizadas con IA')
    analyze_with_ai_action.short_description = "🤖 Analizar con IA"
    
    def clear_alerts_action(self, request, queryset):
        """Limpiar alertas de fotos seleccionadas"""
        queryset.update(has_alerts=False, alert_level='NONE')
        self.message_user(request, '✅ Alertas limpiadas')
    clear_alerts_action.short_description = "🔕 Limpiar Alertas"


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    """Admin para alertas de seguridad"""
    
    list_display = ('employee', 'severity_badge', 'alert_type', 'status_badge', 
                   'created_at', 'acknowledged_by')
    list_filter = ('severity', 'alert_type', 'status', 'created_at')
    search_fields = ('employee__first_name', 'employee__last_name', 'message')
    readonly_fields = ('created_at', 'updated_at', 'acknowledged_at', 'resolved_at', 
                      'ai_data_display', 'photo_preview')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('🚨 Alerta', {
            'fields': ('employee', 'photo', 'photo_preview')
        }),
        ('📋 Detalles', {
            'fields': ('alert_type', 'severity', 'message')
        }),
        ('🤖 Datos IA', {
            'fields': ('ai_data_display',),
            'classes': ('collapse',)
        }),
        ('📊 Estado', {
            'fields': ('status', 'acknowledged_by', 'acknowledged_at', 
                      'resolved_at', 'resolution_notes')
        }),
        ('🕐 Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['acknowledge_action', 'resolve_action', 'mark_false_alarm_action']
    
    def severity_badge(self, obj):
        """Badge de severidad con colores"""
        colors = {
            'LOW': '#10b981',
            'MEDIUM': '#f59e0b',
            'HIGH': '#ef4444',
            'CRITICAL': '#dc2626'
        }
        color = colors.get(obj.severity, '#6b7280')
        
        icons = {
            'LOW': '🟢',
            'MEDIUM': '🟡',
            'HIGH': '🔴',
            'CRITICAL': '🔴🔴'
        }
        icon = icons.get(obj.severity, '⚪')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severidad'
    
    def status_badge(self, obj):
        """Badge de estado"""
        colors = {
            'PENDING': '#f59e0b',
            'ACKNOWLEDGED': '#3b82f6',
            'IN_PROGRESS': '#8b5cf6',
            'RESOLVED': '#10b981',
            'FALSE_ALARM': '#6b7280'
        }
        color = colors.get(obj.status, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def ai_data_display(self, obj):
        """Muestra datos de IA"""
        if not obj.ai_data:
            return '-'
        
        import json
        return format_html(
            '<pre style="background: #f3f4f6; padding: 10px; border-radius: 5px;">{}</pre>',
            json.dumps(obj.ai_data, indent=2, ensure_ascii=False)
        )
    ai_data_display.short_description = 'Datos IA'
    
    def photo_preview(self, obj):
        """Preview de la foto asociada"""
        if obj.photo and obj.photo.thumbnail:
            return format_html('<img src="{}" style="max-height: 100px; border-radius: 5px;" />', obj.photo.thumbnail.url)
        return '-'
    photo_preview.short_description = 'Foto'
    
    def acknowledge_action(self, request, queryset):
        """Reconocer alertas"""
        for alert in queryset:
            alert.acknowledge(request.user)
        self.message_user(request, f'✅ {queryset.count()} alertas reconocidas')
    acknowledge_action.short_description = "✅ Reconocer Alertas"
    
    def resolve_action(self, request, queryset):
        """Resolver alertas"""
        for alert in queryset:
            alert.resolve()
        self.message_user(request, f'✅ {queryset.count()} alertas resueltas')
    resolve_action.short_description = "✓ Resolver Alertas"
    
    def mark_false_alarm_action(self, request, queryset):
        """Marcar como falsa alarma"""
        for alert in queryset:
            alert.mark_false_alarm()
        self.message_user(request, f'✅ {queryset.count()} marcadas como falsas alarmas')
    mark_false_alarm_action.short_description = "⚠️ Marcar Falsa Alarma"


@admin.register(VideoSession)
class VideoSessionAdmin(admin.ModelAdmin):
    """Admin para sesiones de video"""
    
    list_display = ('employee', 'requester', 'status_badge', 'started_at', 
                   'duration_display', 'created_at')
    list_filter = ('status', 'started_at', 'created_at')
    search_fields = ('employee__first_name', 'employee__last_name', 
                    'requester__first_name', 'requester__last_name', 'channel_name')
    readonly_fields = ('created_at', 'updated_at', 'channel_name', 'employee_token', 
                      'requester_token', 'duration_display')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('👥 Participantes', {
            'fields': ('employee', 'requester')
        }),
        ('📹 Sesión de Video', {
            'fields': ('channel_name', 'status', 'started_at', 'ended_at', 'duration_display')
        }),
        ('🔑 Tokens Agora', {
            'fields': ('employee_token', 'requester_token'),
            'classes': ('collapse',)
        }),
        ('📼 Grabación', {
            'fields': ('recording_url',)
        }),
        ('🕐 Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['end_session_action']
    
    def status_badge(self, obj):
        """Badge de estado"""
        colors = {
            'REQUESTED': '#f59e0b',
            'ACTIVE': '#10b981',
            'ENDED': '#6b7280',
            'REJECTED': '#ef4444',
            'TIMEOUT': '#dc2626'
        }
        color = colors.get(obj.status, '#6b7280')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def duration_display(self, obj):
        """Muestra duración formateada"""
        if obj.duration_seconds > 0:
            minutes = obj.duration_seconds // 60
            seconds = obj.duration_seconds % 60
            return f'{minutes}m {seconds}s'
        return '-'
    duration_display.short_description = 'Duración'
    
    def end_session_action(self, request, queryset):
        """Finalizar sesiones activas"""
        count = 0
        for session in queryset.filter(status='ACTIVE'):
            session.end()
            count += 1
        self.message_user(request, f'✅ {count} sesiones finalizadas')
    end_session_action.short_description = "⏹️ Finalizar Sesiones"
