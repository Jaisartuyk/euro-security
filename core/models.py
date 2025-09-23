from django.db import models
from django.contrib.auth.models import User


class BaseModel(models.Model):
    """Modelo base con campos comunes"""
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última Actualización', auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='%(class)s_created', verbose_name='Creado por')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='%(class)s_updated', verbose_name='Actualizado por')
    
    class Meta:
        abstract = True


class Company(models.Model):
    """Modelo para información de la empresa"""
    name = models.CharField('Nombre de la Empresa', max_length=200, default='TV Services')
    legal_name = models.CharField('Razón Social', max_length=200)
    tax_id = models.CharField('RFC/NIT', max_length=20, unique=True)
    address = models.TextField('Dirección')
    city = models.CharField('Ciudad', max_length=100)
    state = models.CharField('Estado', max_length=100)
    country = models.CharField('País', max_length=100, default='México')
    postal_code = models.CharField('Código Postal', max_length=10)
    phone = models.CharField('Teléfono', max_length=20)
    email = models.EmailField('Correo Electrónico')
    website = models.URLField('Sitio Web', blank=True)
    logo = models.ImageField('Logo', upload_to='company/', blank=True)
    
    # Información adicional para empresa de seguridad
    security_license = models.CharField('Licencia de Seguridad', max_length=50, blank=True)
    insurance_policy = models.CharField('Póliza de Seguro', max_length=50, blank=True)
    
    is_active = models.BooleanField('Activa', default=True)
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
    
    def __str__(self):
        return self.name


class SystemConfiguration(models.Model):
    """Configuraciones del sistema"""
    key = models.CharField('Clave', max_length=100, unique=True)
    value = models.TextField('Valor')
    description = models.TextField('Descripción', blank=True)
    is_active = models.BooleanField('Activa', default=True)
    updated_at = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class AuditLog(models.Model):
    """Log de auditoría para cambios importantes"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('LOGIN', 'Iniciar Sesión'),
        ('LOGOUT', 'Cerrar Sesión'),
        ('TRANSFER', 'Transferir'),
        ('APPROVE', 'Aprobar'),
        ('REJECT', 'Rechazar'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                           verbose_name='Usuario')
    action = models.CharField('Acción', max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField('Modelo', max_length=100)
    object_id = models.CharField('ID del Objeto', max_length=100)
    object_repr = models.CharField('Representación del Objeto', max_length=200)
    changes = models.JSONField('Cambios', default=dict, blank=True)
    ip_address = models.GenericIPAddressField('Dirección IP', null=True, blank=True)
    user_agent = models.TextField('User Agent', blank=True)
    timestamp = models.DateTimeField('Fecha y Hora', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.object_repr}"


class Notification(models.Model):
    """Sistema de notificaciones"""
    
    TYPE_CHOICES = [
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('ERROR', 'Error'),
        ('SUCCESS', 'Éxito'),
        ('REMINDER', 'Recordatorio'),
    ]
    
    PRIORITY_CHOICES = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('URGENT', 'Urgente'),
    ]
    
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensaje')
    notification_type = models.CharField('Tipo', max_length=10, choices=TYPE_CHOICES, default='INFO')
    priority = models.CharField('Prioridad', max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    
    # Destinatarios
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='notifications', verbose_name='Destinatario')
    is_global = models.BooleanField('Global', default=False,
                                  help_text='Si está marcado, se mostrará a todos los usuarios')
    
    # Estado
    is_read = models.BooleanField('Leída', default=False)
    is_active = models.BooleanField('Activa', default=True)
    
    # Fechas
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    read_at = models.DateTimeField('Fecha de Lectura', null=True, blank=True)
    expires_at = models.DateTimeField('Fecha de Expiración', null=True, blank=True)
    
    # Metadatos
    related_object_type = models.CharField('Tipo de Objeto Relacionado', max_length=100, blank=True)
    related_object_id = models.CharField('ID del Objeto Relacionado', max_length=100, blank=True)
    action_url = models.URLField('URL de Acción', blank=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient or 'Global'}"
