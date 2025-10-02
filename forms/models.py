from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FormCategory(models.Model):
    """Categorías de formularios"""
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, default='fas fa-file-alt', verbose_name="Icono")
    color = models.CharField(max_length=20, default='primary', verbose_name="Color")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Categoría de Formulario"
        verbose_name_plural = "Categorías de Formularios"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class FormDocument(models.Model):
    """Documentos/Formularios disponibles"""
    PERMISSION_CHOICES = [
        ('admin', 'Solo Administradores'),
        ('hr', 'Recursos Humanos'),
        ('management', 'Gerencia'),
        ('supervisor', 'Supervisores'),
        ('all', 'Todos los empleados'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    category = models.ForeignKey(FormCategory, on_delete=models.CASCADE, verbose_name="Categoría")
    file = models.FileField(upload_to='forms/documents/', verbose_name="Archivo")
    file_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tamaño (bytes)")
    file_type = models.CharField(max_length=10, blank=True, verbose_name="Tipo de archivo")
    
    # Permisos y acceso
    required_permission = models.CharField(
        max_length=20, 
        choices=PERMISSION_CHOICES, 
        default='hr',
        verbose_name="Permiso requerido"
    )
    
    # Metadatos
    version = models.CharField(max_length=20, default='1.0', verbose_name="Versión")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    is_fillable = models.BooleanField(default=False, verbose_name="Formulario rellenable")
    download_count = models.PositiveIntegerField(default=0, verbose_name="Descargas")
    
    # Auditoría
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Creado por")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado")
    
    class Meta:
        verbose_name = "Formulario"
        verbose_name_plural = "Formularios"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def get_file_size_display(self):
        """Mostrar tamaño de archivo en formato legible"""
        if not self.file_size:
            return "N/A"
        
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
    
    def increment_download_count(self):
        """Incrementar contador de descargas"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


class FormDownloadLog(models.Model):
    """Log de descargas de formularios"""
    form = models.ForeignKey(FormDocument, on_delete=models.CASCADE, verbose_name="Formulario")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    downloaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Descargado")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Log de Descarga"
        verbose_name_plural = "Logs de Descargas"
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.form.title} ({self.downloaded_at.strftime('%d/%m/%Y %H:%M')})"
