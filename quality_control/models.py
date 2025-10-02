"""
Modelos para el Sistema de Control de Calidad y Gestión de Riesgos
Euro Security - Sistema Profesional de Gestión de Riesgos
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from employees.models import Employee, Department


class RiskCategory(models.Model):
    """Categorías de Riesgos"""
    
    CATEGORY_TYPES = [
        ('OPERATIVO', 'Riesgos Operativos'),
        ('TECNOLOGICO', 'Riesgos Tecnológicos'),
        ('CAPITAL_HUMANO', 'Riesgos de Capital Humano'),
        ('ENTORNO', 'Riesgos del Entorno y Externos'),
        ('REPUTACIONAL', 'Riesgos Reputacionales'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    category_type = models.CharField(
        max_length=20, 
        choices=CATEGORY_TYPES,
        verbose_name='Tipo de Categoría'
    )
    description = models.TextField(blank=True, verbose_name='Descripción')
    color = models.CharField(
        max_length=7, 
        default='#6c757d',
        help_text='Color en formato HEX (#RRGGBB)',
        verbose_name='Color'
    )
    icon = models.CharField(
        max_length=50, 
        default='fa-exclamation-triangle',
        help_text='Icono de FontAwesome',
        verbose_name='Icono'
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría de Riesgo'
        verbose_name_plural = 'Categorías de Riesgos'
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"


class Risk(models.Model):
    """Riesgos Identificados"""
    
    RISK_LEVELS = [
        ('BAJO', 'Bajo (1-6)'),
        ('MEDIO', 'Medio (7-14)'),
        ('ALTO', 'Alto (15-25)'),
    ]
    
    RISK_COLORS = {
        'BAJO': '#28a745',    # Verde
        'MEDIO': '#ffc107',   # Amarillo
        'ALTO': '#dc3545',    # Rojo
    }
    
    # Información básica
    code = models.CharField(
        max_length=20, 
        unique=True,
        verbose_name='Código',
        help_text='Ej: RSG-001'
    )
    title = models.CharField(max_length=200, verbose_name='Riesgo')
    description = models.TextField(verbose_name='Descripción Detallada')
    category = models.ForeignKey(
        RiskCategory, 
        on_delete=models.PROTECT,
        related_name='risks',
        verbose_name='Categoría'
    )
    
    # Evaluación del riesgo
    probability = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Probabilidad (1-5)',
        help_text='1=Muy Bajo, 2=Bajo, 3=Medio, 4=Alto, 5=Muy Alto'
    )
    impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Impacto (1-5)',
        help_text='1=Muy Bajo, 2=Bajo, 3=Medio, 4=Alto, 5=Muy Alto'
    )
    risk_score = models.IntegerField(
        editable=False,
        verbose_name='Nivel de Riesgo (P×I)'
    )
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_LEVELS,
        editable=False,
        verbose_name='Nivel de Riesgo'
    )
    
    # Responsables
    responsible = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_risks',
        verbose_name='Responsable'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Departamento Afectado'
    )
    
    # Estado y seguimiento
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_mitigated = models.BooleanField(default=False, verbose_name='Mitigado')
    mitigation_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Mitigación')
    
    # Auditoría
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_risks',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    last_review_date = models.DateField(null=True, blank=True, verbose_name='Última Revisión')
    next_review_date = models.DateField(null=True, blank=True, verbose_name='Próxima Revisión')
    
    class Meta:
        verbose_name = 'Riesgo'
        verbose_name_plural = 'Riesgos'
        ordering = ['-risk_score', 'title']
        indexes = [
            models.Index(fields=['risk_level', 'is_active']),
            models.Index(fields=['category', 'risk_score']),
        ]
    
    def save(self, *args, **kwargs):
        # Calcular nivel de riesgo automáticamente
        self.risk_score = self.probability * self.impact
        
        # Determinar nivel de riesgo
        if self.risk_score <= 6:
            self.risk_level = 'BAJO'
        elif self.risk_score <= 14:
            self.risk_level = 'MEDIO'
        else:
            self.risk_level = 'ALTO'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"[{self.code}] {self.title}"
    
    def get_risk_color(self):
        """Retorna el color según el nivel de riesgo"""
        return self.RISK_COLORS.get(self.risk_level, '#6c757d')
    
    def get_probability_label(self):
        """Etiqueta de probabilidad"""
        labels = {1: 'Muy Bajo', 2: 'Bajo', 3: 'Medio', 4: 'Alto', 5: 'Muy Alto'}
        return labels.get(self.probability, 'N/A')
    
    def get_impact_label(self):
        """Etiqueta de impacto"""
        labels = {1: 'Muy Bajo', 2: 'Bajo', 3: 'Medio', 4: 'Alto', 5: 'Muy Alto'}
        return labels.get(self.impact, 'N/A')


class ControlMeasure(models.Model):
    """Medidas de Control y Acción"""
    
    STATUS_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROGRESO', 'En Progreso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    PRIORITY_CHOICES = [
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('CRITICA', 'Crítica'),
    ]
    
    risk = models.ForeignKey(
        Risk,
        on_delete=models.CASCADE,
        related_name='control_measures',
        verbose_name='Riesgo'
    )
    title = models.CharField(max_length=200, verbose_name='Medida de Control')
    description = models.TextField(verbose_name='Descripción Detallada')
    
    # Prioridad y estado
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIA',
        verbose_name='Prioridad'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado'
    )
    
    # Responsables y fechas
    responsible = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='control_measures',
        verbose_name='Responsable'
    )
    start_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Inicio')
    due_date = models.DateField(null=True, blank=True, verbose_name='Fecha Límite')
    completion_date = models.DateField(null=True, blank=True, verbose_name='Fecha de Completación')
    
    # Costos y recursos
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo Estimado'
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Costo Real'
    )
    
    # Efectividad
    effectiveness_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Efectividad (1-10)',
        help_text='Calificación de la efectividad de la medida'
    )
    
    # Auditoría
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_measures',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Medida de Control'
        verbose_name_plural = 'Medidas de Control'
        ordering = ['-priority', 'due_date']
    
    def __str__(self):
        return f"{self.risk.code} - {self.title}"
    
    def is_overdue(self):
        """Verifica si la medida está vencida"""
        if self.due_date and self.status not in ['COMPLETADA', 'CANCELADA']:
            return timezone.now().date() > self.due_date
        return False


class RiskAssessment(models.Model):
    """Evaluaciones Periódicas de Riesgos"""
    
    risk = models.ForeignKey(
        Risk,
        on_delete=models.CASCADE,
        related_name='assessments',
        verbose_name='Riesgo'
    )
    assessment_date = models.DateField(default=timezone.now, verbose_name='Fecha de Evaluación')
    
    # Evaluación
    probability = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Probabilidad'
    )
    impact = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Impacto'
    )
    risk_score = models.IntegerField(editable=False, verbose_name='Puntuación')
    
    # Observaciones
    observations = models.TextField(blank=True, verbose_name='Observaciones')
    recommendations = models.TextField(blank=True, verbose_name='Recomendaciones')
    
    # Auditoría
    assessed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Evaluado por'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Evaluación de Riesgo'
        verbose_name_plural = 'Evaluaciones de Riesgos'
        ordering = ['-assessment_date']
    
    def save(self, *args, **kwargs):
        self.risk_score = self.probability * self.impact
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.risk.code} - {self.assessment_date}"


class RiskIncident(models.Model):
    """Incidentes Relacionados con Riesgos"""
    
    SEVERITY_CHOICES = [
        ('MENOR', 'Menor'),
        ('MODERADO', 'Moderado'),
        ('GRAVE', 'Grave'),
        ('CRITICO', 'Crítico'),
    ]
    
    risk = models.ForeignKey(
        Risk,
        on_delete=models.CASCADE,
        related_name='incidents',
        verbose_name='Riesgo Relacionado'
    )
    incident_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de Incidente'
    )
    title = models.CharField(max_length=200, verbose_name='Título del Incidente')
    description = models.TextField(verbose_name='Descripción')
    
    # Detalles del incidente
    incident_date = models.DateTimeField(verbose_name='Fecha y Hora del Incidente')
    location = models.CharField(max_length=200, blank=True, verbose_name='Ubicación')
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        verbose_name='Severidad'
    )
    
    # Personas involucradas
    reported_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_incidents',
        verbose_name='Reportado por'
    )
    affected_employees = models.ManyToManyField(
        Employee,
        blank=True,
        related_name='affected_by_incidents',
        verbose_name='Empleados Afectados'
    )
    
    # Impacto
    financial_impact = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Impacto Financiero'
    )
    operational_impact = models.TextField(blank=True, verbose_name='Impacto Operacional')
    
    # Resolución
    is_resolved = models.BooleanField(default=False, verbose_name='Resuelto')
    resolution_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Resolución')
    resolution_notes = models.TextField(blank=True, verbose_name='Notas de Resolución')
    
    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Incidente de Riesgo'
        verbose_name_plural = 'Incidentes de Riesgos'
        ordering = ['-incident_date']
    
    def __str__(self):
        return f"[{self.incident_number}] {self.title}"
