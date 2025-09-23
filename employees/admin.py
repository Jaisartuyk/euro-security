from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'get_full_name', 'email', 'department', 'position', 'hire_date', 'is_active')
    list_filter = ('department', 'position', 'is_active', 'hire_date')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'user__username')
    ordering = ('employee_id',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('user', 'employee_id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Información Laboral', {
            'fields': ('department', 'position', 'hire_date', 'salary', 'is_active')
        }),
        ('Información Adicional', {
            'fields': ('address', 'emergency_contact', 'emergency_phone', 'notes')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Nombre Completo'
    
    def save_model(self, request, obj, form, change):
        # Si no tiene usuario asociado, crear uno
        if not obj.user and obj.email:
            try:
                # Buscar usuario existente por email
                user = User.objects.get(email=obj.email)
                obj.user = user
            except User.DoesNotExist:
                # Crear nuevo usuario
                username = obj.email.split('@')[0]
                # Asegurar que el username sea único
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=obj.email,
                    first_name=obj.first_name,
                    last_name=obj.last_name,
                    password='temp123456'  # Contraseña temporal
                )
                obj.user = user
        
        super().save_model(request, obj, form, change)

# Personalizar el admin de User para mostrar empleados relacionados
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Perfil de Empleado'
    fk_name = 'user'
    
    fields = ('employee_id', 'department', 'position', 'phone', 'hire_date', 'is_active')

class CustomUserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Re-registrar User admin con el personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
