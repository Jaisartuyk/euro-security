from django.contrib import admin
from .models import Department, DepartmentBudget


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department_type', 'manager', 'get_employee_count', 'budget', 'is_active']
    list_filter = ['department_type', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'code', 'department_type', 'description')
        }),
        ('Gestión', {
            'fields': ('manager', 'budget', 'is_active')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_employee_count(self, obj):
        return obj.get_employee_count()
    get_employee_count.short_description = 'Empleados'


@admin.register(DepartmentBudget)
class DepartmentBudgetAdmin(admin.ModelAdmin):
    list_display = ['department', 'year', 'month', 'allocated_budget', 'spent_budget', 'remaining_budget']
    list_filter = ['year', 'month', 'department']
    search_fields = ['department__name', 'notes']
    
    def remaining_budget(self, obj):
        return obj.remaining_budget
    remaining_budget.short_description = 'Presupuesto Restante'
