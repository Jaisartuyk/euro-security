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
    form = models.ForeignKey(FormDocument, on_delete=models.CASCADE, related_name='download_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, default='127.0.0.1')
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-downloaded_at']
        verbose_name = 'Log de Descarga'
        verbose_name_plural = 'Logs de Descargas'
    
    def __str__(self):
        return f'{self.user.username} - {self.form.title} - {self.downloaded_at.strftime("%d/%m/%Y %H:%M")}'


# ============================================================================ 
# SISTEMA DE FORMULARIOS DINÁMICOS
# ============================================================================

class FormTemplate(models.Model):
    """Plantilla de formulario dinámico"""
    FIELD_TYPES = [
        ('text', 'Texto'),
        ('textarea', 'Área de Texto'),
        ('email', 'Email'),
        ('number', 'Número'),
        ('date', 'Fecha'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio Button'),
        ('select', 'Lista Desplegable'),
        ('file', 'Archivo'),
        ('signature', 'Firma Digital'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    category = models.ForeignKey(FormCategory, on_delete=models.CASCADE, verbose_name='Categoría')
    code = models.CharField(max_length=20, unique=True, verbose_name='Código')
    version = models.CharField(max_length=10, default='1.0', verbose_name='Versión')
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    requires_approval = models.BooleanField(default=True, verbose_name='Requiere Aprobación')
    allow_draft = models.BooleanField(default=True, verbose_name='Permitir Borrador')
    required_permission = models.CharField(max_length=20, choices=FormDocument.PERMISSION_CHOICES, default='all')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Estadísticas
    submission_count = models.PositiveIntegerField(default=0, verbose_name='Envíos')
    
    class Meta:
        ordering = ['category', 'title']
        verbose_name = 'Plantilla de Formulario'
        verbose_name_plural = 'Plantillas de Formularios'
    
    def __str__(self):
        return f'{self.code} - {self.title}'
    
    def increment_submission_count(self):
        self.submission_count += 1
        self.save(update_fields=['submission_count'])


class FormField(models.Model):
    """Campo de formulario dinámico"""
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='fields')
    
    # Configuración del campo
    name = models.CharField(max_length=100, verbose_name='Nombre del Campo')
    label = models.CharField(max_length=200, verbose_name='Etiqueta')
    field_type = models.CharField(max_length=20, choices=FormTemplate.FIELD_TYPES, verbose_name='Tipo')
    placeholder = models.CharField(max_length=200, blank=True, verbose_name='Placeholder')
    help_text = models.CharField(max_length=300, blank=True, verbose_name='Texto de Ayuda')
    
    # Validaciones
    is_required = models.BooleanField(default=False, verbose_name='Requerido')
    min_length = models.PositiveIntegerField(null=True, blank=True, verbose_name='Longitud Mínima')
    max_length = models.PositiveIntegerField(null=True, blank=True, verbose_name='Longitud Máxima')
    
    # Opciones para select/radio
    choices = models.JSONField(default=list, blank=True, verbose_name='Opciones')
    
    # Orden y agrupación
    order = models.PositiveIntegerField(default=0, verbose_name='Orden')
    section = models.CharField(max_length=100, blank=True, verbose_name='Sección')
    
    class Meta:
        ordering = ['template', 'order', 'name']
        unique_together = ['template', 'name']
        verbose_name = 'Campo de Formulario'
        verbose_name_plural = 'Campos de Formulario'
    
    def __str__(self):
        return f'{self.template.code} - {self.label}'


class FormSubmission(models.Model):
    """Envío de formulario completado"""
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('submitted', 'Enviado'),
        ('under_review', 'En Revisión'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('completed', 'Completado'),
    ]
    
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='submissions')
    
    # Participantes
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='form_submissions', verbose_name='Enviado por')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_forms', verbose_name='Asignado por')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_forms', verbose_name='Revisado por')
    
    # Estado y fechas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Estado')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Envío')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Revisión')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Datos del formulario
    form_data = models.JSONField(default=dict, verbose_name='Datos del Formulario')
    
    # Comentarios y notas
    notes = models.TextField(blank=True, verbose_name='Notas')
    review_comments = models.TextField(blank=True, verbose_name='Comentarios de Revisión')
    
    # Archivos adjuntos
    attachments = models.JSONField(default=list, blank=True, verbose_name='Archivos Adjuntos')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Envío de Formulario'
        verbose_name_plural = 'Envíos de Formularios'
    
    def __str__(self):
        return f'{self.template.code} - {self.submitted_by.get_full_name() or self.submitted_by.username} - {self.get_status_display()}'
    
    def save(self, *args, **kwargs):
        # Actualizar fecha de envío cuando cambia a submitted
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        
        # Actualizar fecha de revisión cuando se aprueba/rechaza
        if self.status in ['approved', 'rejected'] and not self.reviewed_at:
            self.reviewed_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Incrementar contador en template
        if self.status == 'submitted':
            self.template.increment_submission_count()
    
    def get_field_value(self, field_name):
        """Obtener valor de un campo específico"""
        return self.form_data.get(field_name, '')
    
    def set_field_value(self, field_name, value):
        """Establecer valor de un campo específico"""
        self.form_data[field_name] = value
        self.save(update_fields=['form_data', 'updated_at'])


class FormAssignment(models.Model):
    """Asignación de formulario a empleado"""
    template = models.ForeignKey(FormTemplate, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_forms_to_complete')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forms_assigned_by_me')
    
    # Configuración
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha Límite')
    priority = models.CharField(max_length=10, choices=[('low', 'Baja'), ('medium', 'Media'), ('high', 'Alta')], default='medium')
    instructions = models.TextField(blank=True, verbose_name='Instrucciones')
    
    # Estado
    is_completed = models.BooleanField(default=False, verbose_name='Completado')
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Relación con submission
    submission = models.OneToOneField(FormSubmission, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignment')
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['template', 'assigned_to', 'assigned_by']
        verbose_name = 'Asignación de Formulario'
        verbose_name_plural = 'Asignaciones de Formularios'
    
    def __str__(self):
        return f'{self.template.code} → {self.assigned_to.get_full_name() or self.assigned_to.username}'
    
    def mark_completed(self, submission):
        """Marcar asignación como completada"""
        self.is_completed = True
        self.completed_at = timezone.now()
        self.submission = submission
        self.save()
