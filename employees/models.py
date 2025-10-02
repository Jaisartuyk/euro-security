from django.db import models
from django.contrib.auth.models import User, Group
from core.models import BaseModel
import uuid
import secrets
import string


class Employee(BaseModel):
    """Modelo para los empleados de la empresa"""
    
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Soltero/a'),
        ('MARRIED', 'Casado/a'),
        ('DIVORCED', 'Divorciado/a'),
        ('WIDOWED', 'Viudo/a'),
        ('OTHER', 'Otro'),
    ]
    
    # Información básica
    employee_id = models.CharField('ID Empleado', max_length=20, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Usuario del Sistema')
    
    # Información personal
    first_name = models.CharField('Nombres', max_length=100)
    last_name = models.CharField('Apellidos', max_length=100)
    email = models.EmailField('Correo Electrónico', unique=True)
    phone = models.CharField('Teléfono', max_length=15)
    
    # Documentos de identidad
    national_id = models.CharField('Cédula/DNI', max_length=20, unique=True)
    
    # Información demográfica
    date_of_birth = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    gender = models.CharField('Género', max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    marital_status = models.CharField('Estado Civil', max_length=10, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    
    # Dirección
    address = models.TextField('Dirección', null=True, blank=True)
    city = models.CharField('Ciudad', max_length=100, null=True, blank=True)
    country = models.CharField('País', max_length=100, default='México')
    
    # Información laboral - usando strings para evitar importaciones circulares
    department = models.ForeignKey('departments.Department', on_delete=models.PROTECT, 
                                 related_name='employees', verbose_name='Departamento')
    position = models.ForeignKey('positions.Position', on_delete=models.PROTECT, 
                               related_name='employees', verbose_name='Puesto')
    hire_date = models.DateField('Fecha de Contratación')
    
    # Información salarial
    current_salary = models.DecimalField('Salario Actual', max_digits=10, decimal_places=2)
    
    # Estado
    is_active = models.BooleanField('Activo', default=True)
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.employee_id} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Retorna el nombre completo del empleado"""
        return f"{self.first_name} {self.last_name}"
    
    def generate_secure_password(self, length=12):
        """Genera una contraseña segura"""
        alphabet = string.ascii_letters + string.digits + "!@#$%&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    def create_user_account(self):
        """Crea una cuenta de usuario para el empleado"""
        if not self.user:
            # Generar username único basado en nombre y employee_id
            base_username = f"{self.first_name.lower()}.{self.last_name.lower()}"
            username = base_username[:20]  # Limitar longitud
            
            # Asegurar que el username sea único
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
            
            # Generar contraseña segura
            password = self.generate_secure_password()
            
            # Crear usuario
            user = User.objects.create_user(
                username=username,
                email=self.email,
                password=password,
                first_name=self.first_name,
                last_name=self.last_name,
                is_active=self.is_active
            )
            
            # Asignar grupo según el nivel del puesto
            self.assign_user_group(user)
            
            self.user = user
            self.save(update_fields=['user'])
            
            return {
                'username': username,
                'password': password,
                'user': user
            }
        return None
    
    def assign_user_group(self, user):
        """Asigna el grupo apropiado según el nivel del puesto"""
        if self.position:
            level = self.position.level
            
            # Mapear niveles a grupos
            group_mapping = {
                'DIRECTOR': 'Directores',
                'MANAGER': 'Gerentes',
                'LEAD': 'Supervisores',
                'SENIOR': 'Empleados Senior',
                'JUNIOR': 'Empleados Junior',
                'ENTRY': 'Empleados Básicos'
            }
            
            group_name = group_mapping.get(level, 'Empleados Básicos')
            
            # Crear grupo si no existe
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Asignar usuario al grupo
            user.groups.add(group)
    
    def get_permission_level(self):
        """Retorna el nivel de permisos del empleado"""
        # Superusers siempre tienen permisos completos
        if self.user and self.user.is_superuser:
            return 'full'
        
        if not self.position:
            return 'basic'
        
        level_permissions = {
            'EXECUTIVE': 'full',  # Nivel ejecutivo (CEO, CFO, etc.)
            'DIRECTOR': 'full',
            'COORDINACION': 'management',  # Coordinadores tienen permisos de gestión
            'MANAGER': 'management',
            'LEAD': 'supervisor',
            'SENIOR': 'advanced',
            'JUNIOR': 'standard',
            'ENTRY': 'basic'
        }
        
        return level_permissions.get(self.position.level, 'basic')
    
    def can_view_all_employees(self):
        """Determina si puede ver todos los empleados"""
        return self.get_permission_level() in ['full', 'management', 'advanced']
    
    def can_edit_employees(self):
        """Determina si puede editar empleados"""
        return self.get_permission_level() in ['full', 'management', 'advanced']
    
    def can_view_reports(self):
        """Determina si puede ver reportes"""
        return self.get_permission_level() in ['full', 'management', 'supervisor']
    
    def can_view_payroll(self):
        """Determina si puede ver información de nómina"""
        return self.get_permission_level() in ['full', 'management']
    
    def reset_user_password(self):
        """Resetea la contraseña del usuario asociado"""
        if self.user:
            # Generar nueva contraseña segura
            new_password = self.generate_secure_password()
            
            # Cambiar la contraseña
            self.user.set_password(new_password)
            self.user.save()
            
            return {
                'username': self.user.username,
                'password': new_password,
                'user': self.user
            }
        return None
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            # Generar ID único para el empleado
            self.employee_id = f"EMP{str(uuid.uuid4().int)[:8]}"
        super().save(*args, **kwargs)
