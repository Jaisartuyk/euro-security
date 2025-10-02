from django.contrib import admin
from django.utils.html import format_html
from .models import (
    FormCategory, FormDocument, FormDownloadLog,
    FormTemplate, FormField, FormSubmission, FormAssignment
)
import os

@admin.register(FormCategory)
class FormCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon_display', 'color_display', 'order', 'is_active', 'form_count']
    list_filter = ['is_active', 'color']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    
    def icon_display(self, obj):
        return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)
    icon_display.short_description = 'Icono'
    
    def color_display(self, obj):
        return format_html('<span class="badge bg-{}">{}</span>', obj.color, obj.color)
    color_display.short_description = 'Color'
    
    def form_count(self, obj):
        return obj.formdocument_set.count()
    form_count.short_description = 'Formularios'


@admin.register(FormDocument)
class FormDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'version', 'required_permission', 'file_size_display', 
                   'download_count', 'is_active', 'created_at']
    list_filter = ['category', 'required_permission', 'is_active', 'is_fillable', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['file_size', 'file_type', 'download_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'category')
        }),
        ('Archivo', {
            'fields': ('file', 'file_size', 'file_type')
        }),
        ('Permisos y Configuración', {
            'fields': ('required_permission', 'version', 'is_active', 'is_fillable')
        }),
        ('Estadísticas', {
            'fields': ('download_count',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Solo al crear
            obj.created_by = request.user
            
        # Obtener información del archivo
        if obj.file:
            obj.file_size = obj.file.size
            obj.file_type = obj.file.name.split('.')[-1].upper() if '.' in obj.file.name else 'UNKNOWN'
            
        super().save_model(request, obj, form, change)
    
    def file_size_display(self, obj):
        return obj.get_file_size_display()
    file_size_display.short_description = 'Tamaño'


@admin.register(FormDownloadLog)
class FormDownloadLogAdmin(admin.ModelAdmin):
    list_display = ['form', 'user', 'downloaded_at', 'ip_address']
    list_filter = ['downloaded_at', 'form__category']
    search_fields = ['form__title', 'user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['form', 'user', 'downloaded_at', 'ip_address', 'user_agent']
    
    def has_add_permission(self, request):
        return False  # No permitir crear logs manualmente
    
    def has_change_permission(self, request, obj=None):
        return False  # Solo lectura


# ============================================================================
# ADMIN PARA FORMULARIOS DINÁMICOS
# ============================================================================

class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1
    fields = ['name', 'label', 'field_type', 'is_required', 'order', 'section']
    ordering = ['order', 'name']


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'category', 'version', 'is_active', 'submission_count', 'created_at']
    list_filter = ['category', 'is_active', 'requires_approval', 'required_permission', 'created_at']
    search_fields = ['code', 'title', 'description']
    readonly_fields = ['submission_count', 'created_at', 'updated_at']
    inlines = [FormFieldInline]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'category', 'code', 'version')
        }),
        ('Configuración', {
            'fields': ('is_active', 'requires_approval', 'allow_draft', 'required_permission')
        }),
        ('Estadísticas', {
            'fields': ('submission_count',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['template', 'name', 'label', 'field_type', 'is_required', 'order', 'section']
    list_filter = ['template', 'field_type', 'is_required', 'section']
    search_fields = ['template__title', 'name', 'label']
    ordering = ['template', 'order', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('template', 'name', 'label', 'field_type')
        }),
        ('Configuración', {
            'fields': ('placeholder', 'help_text', 'is_required')
        }),
        ('Validaciones', {
            'fields': ('min_length', 'max_length', 'choices'),
            'classes': ('collapse',)
        }),
        ('Organización', {
            'fields': ('order', 'section')
        })
    )


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['template', 'submitted_by', 'status', 'submitted_at', 'reviewed_by', 'created_at']
    list_filter = ['template', 'status', 'submitted_at', 'reviewed_at', 'created_at']
    search_fields = ['template__title', 'submitted_by__username', 'submitted_by__first_name', 'submitted_by__last_name']
    readonly_fields = ['form_data', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('template', 'submitted_by', 'assigned_by')
        }),
        ('Estado', {
            'fields': ('status', 'submitted_at', 'reviewed_by', 'reviewed_at')
        }),
        ('Datos del Formulario', {
            'fields': ('form_data',),
            'classes': ('collapse',)
        }),
        ('Comentarios', {
            'fields': ('notes', 'review_comments')
        }),
        ('Archivos', {
            'fields': ('attachments',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data:
            if obj.status in ['approved', 'rejected'] and not obj.reviewed_by:
                obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FormAssignment)
class FormAssignmentAdmin(admin.ModelAdmin):
    list_display = ['template', 'assigned_to', 'assigned_by', 'priority', 'due_date', 'is_completed', 'created_at']
    list_filter = ['template', 'priority', 'is_completed', 'due_date', 'created_at']
    search_fields = ['template__title', 'assigned_to__username', 'assigned_to__first_name', 'assigned_to__last_name']
    readonly_fields = ['is_completed', 'completed_at', 'submission', 'created_at']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('template', 'assigned_to', 'assigned_by')
        }),
        ('Configuración', {
            'fields': ('due_date', 'priority', 'instructions')
        }),
        ('Estado', {
            'fields': ('is_completed', 'completed_at', 'submission'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)
