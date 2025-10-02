"""
Admin para el Sistema de Control de Calidad y Gestión de Riesgos
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import RiskCategory, Risk, ControlMeasure, RiskAssessment, RiskIncident


@admin.register(RiskCategory)
class RiskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'colored_badge', 'is_active']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'description']
    
    def colored_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">'
            '<i class="{}"></i> {}</span>',
            obj.color,
            obj.icon,
            obj.get_category_type_display()
        )
    colored_badge.short_description = 'Tipo'


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'category', 'probability', 'impact', 'risk_score_badge', 'responsible', 'is_active']
    list_filter = ['risk_level', 'category', 'is_active', 'is_mitigated']
    search_fields = ['code', 'title', 'description']
    readonly_fields = ['risk_score', 'risk_level', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'title', 'description', 'category')
        }),
        ('Evaluación del Riesgo', {
            'fields': ('probability', 'impact', 'risk_score', 'risk_level')
        }),
        ('Responsables', {
            'fields': ('responsible', 'department')
        }),
        ('Estado y Seguimiento', {
            'fields': ('is_active', 'is_mitigated', 'mitigation_date', 'last_review_date', 'next_review_date')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def risk_score_badge(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">'
            '{} - {}</span>',
            obj.get_risk_color(),
            obj.risk_score,
            obj.get_risk_level_display()
        )
    risk_score_badge.short_description = 'Nivel de Riesgo'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ControlMeasure)
class ControlMeasureAdmin(admin.ModelAdmin):
    list_display = ['title', 'risk', 'priority_badge', 'status_badge', 'responsible', 'due_date', 'is_overdue_badge']
    list_filter = ['priority', 'status', 'due_date']
    search_fields = ['title', 'description', 'risk__title']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('risk', 'title', 'description')
        }),
        ('Prioridad y Estado', {
            'fields': ('priority', 'status')
        }),
        ('Responsables y Fechas', {
            'fields': ('responsible', 'start_date', 'due_date', 'completion_date')
        }),
        ('Costos y Efectividad', {
            'fields': ('estimated_cost', 'actual_cost', 'effectiveness_score')
        }),
    )
    
    def priority_badge(self, obj):
        colors = {
            'BAJA': '#28a745',
            'MEDIA': '#ffc107',
            'ALTA': '#fd7e14',
            'CRITICA': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridad'
    
    def status_badge(self, obj):
        colors = {
            'PENDIENTE': '#6c757d',
            'EN_PROGRESO': '#007bff',
            'COMPLETADA': '#28a745',
            'CANCELADA': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue():
            return format_html('<span style="color: red; font-weight: bold;">⚠️ Vencida</span>')
        return format_html('<span style="color: green;">✓ A tiempo</span>')
    is_overdue_badge.short_description = 'Estado de Plazo'


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['risk', 'assessment_date', 'probability', 'impact', 'risk_score', 'assessed_by']
    list_filter = ['assessment_date', 'assessed_by']
    search_fields = ['risk__title', 'observations']
    readonly_fields = ['risk_score', 'created_at']


@admin.register(RiskIncident)
class RiskIncidentAdmin(admin.ModelAdmin):
    list_display = ['incident_number', 'title', 'risk', 'severity_badge', 'incident_date', 'is_resolved_badge']
    list_filter = ['severity', 'is_resolved', 'incident_date']
    search_fields = ['incident_number', 'title', 'description']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('risk', 'incident_number', 'title', 'description')
        }),
        ('Detalles del Incidente', {
            'fields': ('incident_date', 'location', 'severity')
        }),
        ('Personas Involucradas', {
            'fields': ('reported_by', 'affected_employees')
        }),
        ('Impacto', {
            'fields': ('financial_impact', 'operational_impact')
        }),
        ('Resolución', {
            'fields': ('is_resolved', 'resolution_date', 'resolution_notes')
        }),
    )
    
    def severity_badge(self, obj):
        colors = {
            'MENOR': '#28a745',
            'MODERADO': '#ffc107',
            'GRAVE': '#fd7e14',
            'CRITICO': '#dc3545'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.severity, '#6c757d'),
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severidad'
    
    def is_resolved_badge(self, obj):
        if obj.is_resolved:
            return format_html('<span style="color: green; font-weight: bold;">✓ Resuelto</span>')
        return format_html('<span style="color: orange; font-weight: bold;">⏳ Pendiente</span>')
    is_resolved_badge.short_description = 'Estado'
