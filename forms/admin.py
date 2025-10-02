from django.contrib import admin
from django.utils.html import format_html
from .models import FormCategory, FormDocument, FormDownloadLog


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
