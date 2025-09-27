"""
Modelos para el sistema médico con IA - Dr. Claude
EURO SECURITY - Asistente Médico Inteligente
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Employee
import json


class MedicalDocumentType(models.TextChoices):
    """Tipos de documentos médicos"""
    CERTIFICATE = 'certificate', 'Certificado Médico'
    PRESCRIPTION = 'prescription', 'Receta Médica'
    LAB_RESULT = 'lab_result', 'Resultado de Laboratorio'
    MEDICAL_REPORT = 'medical_report', 'Informe Médico'
    DISABILITY_CERT = 'disability_cert', 'Certificado de Discapacidad'
    VACCINATION = 'vaccination', 'Certificado de Vacunación'


class MedicalLeaveStatus(models.TextChoices):
    """Estados de permisos médicos"""
    PENDING = 'pending', 'Pendiente'
    AI_APPROVED = 'ai_approved', 'Aprobado por IA'
    AI_REJECTED = 'ai_rejected', 'Rechazado por IA'
    HUMAN_REVIEW = 'human_review', 'Revisión Humana'
    HR_APPROVED = 'hr_approved', 'Aprobado por RRHH'
    HR_REJECTED = 'hr_rejected', 'Rechazado por RRHH'
    ACTIVE = 'active', 'Activo'
    COMPLETED = 'completed', 'Completado'
    CANCELLED = 'cancelled', 'Cancelado'


class MedicalDocument(models.Model):
    """Documentos médicos subidos por empleados"""
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='medical_documents'
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=MedicalDocumentType.choices,
        default=MedicalDocumentType.CERTIFICATE
    )
    
    # Archivo del documento
    document_file = models.FileField(
        upload_to='medical_documents/%Y/%m/',
        help_text='Certificado médico, receta, etc.'
    )
    
    # Datos extraídos por IA
    ai_extracted_data = models.JSONField(
        default=dict,
        help_text='Datos extraídos automáticamente por Dr. Claude'
    )
    
    # Análisis de IA
    ai_analysis = models.TextField(
        blank=True,
        help_text='Análisis completo realizado por Dr. Claude'
    )
    
    ai_confidence_score = models.FloatField(
        default=0.0,
        help_text='Nivel de confianza de la IA (0.0 - 1.0)'
    )
    
    # Validación
    is_valid_document = models.BooleanField(default=False)
    validation_notes = models.TextField(blank=True)
    
    # Metadatos
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by_ai = models.BooleanField(default=False)
    
    # Información médica extraída
    patient_name = models.CharField(max_length=200, blank=True)
    diagnosis = models.TextField(blank=True)
    doctor_name = models.CharField(max_length=200, blank=True)
    medical_center = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'attendance_medical_document'
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_document_type_display()}"
    
    def get_extracted_data(self, key, default=None):
        """Obtener dato específico extraído por IA"""
        return self.ai_extracted_data.get(key, default)
    
    def set_extracted_data(self, key, value):
        """Establecer dato extraído por IA"""
        if not isinstance(self.ai_extracted_data, dict):
            self.ai_extracted_data = {}
        self.ai_extracted_data[key] = value
        
    def mark_as_processed(self):
        """Marcar como procesado por IA"""
        self.processed_at = timezone.now()
        self.processed_by_ai = True
        self.save()


class MedicalLeave(models.Model):
    """Permisos médicos generados automáticamente"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='medical_leaves'
    )
    
    medical_document = models.ForeignKey(
        MedicalDocument,
        on_delete=models.CASCADE,
        related_name='leaves'
    )
    
    # Fechas del permiso
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField(default=0)
    
    # Estado y aprobación
    status = models.CharField(
        max_length=20,
        choices=MedicalLeaveStatus.choices,
        default=MedicalLeaveStatus.PENDING
    )
    
    # Procesamiento IA
    ai_recommendation = models.CharField(
        max_length=20,
        choices=[
            ('approve', 'Aprobar'),
            ('reject', 'Rechazar'), 
            ('review', 'Requiere Revisión Humana')
        ],
        blank=True
    )
    
    ai_reasoning = models.TextField(
        blank=True,
        help_text='Razonamiento de Dr. Claude para la decisión'
    )
    
    # Información médica
    diagnosis_summary = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)
    
    # Aprobación humana
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_medical_leaves'
    )
    
    reviewed_at = models.DateTimeField(null=True, blank=True)
    hr_notes = models.TextField(blank=True)
    
    # Impacto en turnos
    shifts_affected = models.JSONField(
        default=list,
        help_text='IDs de turnos afectados por este permiso'
    )
    
    automatic_reassignment = models.BooleanField(
        default=False,
        help_text='Si se reasignaron turnos automáticamente'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_medical_leave'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.start_date} a {self.end_date}"
    
    def calculate_total_days(self):
        """Calcular días totales del permiso"""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            self.total_days = delta.days + 1
        return self.total_days
    
    def approve_automatically(self, ai_reasoning=""):
        """Aprobar automáticamente por IA"""
        self.status = MedicalLeaveStatus.AI_APPROVED
        self.ai_recommendation = 'approve'
        self.ai_reasoning = ai_reasoning
        self.save()
        
    def require_human_review(self, ai_reasoning=""):
        """Marcar para revisión humana"""
        self.status = MedicalLeaveStatus.HUMAN_REVIEW
        self.ai_recommendation = 'review'
        self.ai_reasoning = ai_reasoning
        self.save()
        
    def approve_by_hr(self, user, notes=""):
        """Aprobar por RRHH"""
        self.status = MedicalLeaveStatus.HR_APPROVED
        self.reviewed_by = user
        self.reviewed_at = timezone.now()
        self.hr_notes = notes
        self.save()


class DrClaudeConversation(models.Model):
    """Conversaciones con Dr. Claude"""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='claude_conversations'
    )
    
    session_id = models.CharField(
        max_length=100,
        help_text='ID único de la sesión de chat'
    )
    
    # Mensaje
    user_message = models.TextField()
    claude_response = models.TextField()
    
    # Contexto
    conversation_context = models.JSONField(
        default=dict,
        help_text='Contexto de la conversación para Dr. Claude'
    )
    
    # Metadatos
    timestamp = models.DateTimeField(auto_now_add=True)
    response_time_ms = models.IntegerField(default=0)
    
    # Clasificación del mensaje
    message_type = models.CharField(
        max_length=50,
        choices=[
            ('medical_query', 'Consulta Médica'),
            ('document_upload', 'Subida de Documento'),
            ('policy_question', 'Pregunta de Política'),
            ('general_help', 'Ayuda General'),
            ('complaint', 'Queja o Reclamo'),
        ],
        blank=True
    )
    
    # Satisfacción
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text='Calificación del usuario (1-5 estrellas)'
    )
    
    class Meta:
        db_table = 'attendance_claude_conversation'
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class MedicalAnalytics(models.Model):
    """Analytics y métricas del sistema médico"""
    
    # Período de análisis
    date = models.DateField(unique=True)
    
    # Métricas de documentos
    documents_uploaded = models.IntegerField(default=0)
    documents_processed = models.IntegerField(default=0)
    documents_approved = models.IntegerField(default=0)
    documents_rejected = models.IntegerField(default=0)
    documents_pending_review = models.IntegerField(default=0)
    
    # Métricas de IA
    ai_accuracy_rate = models.FloatField(default=0.0)
    ai_processing_time_avg = models.FloatField(default=0.0)
    human_intervention_rate = models.FloatField(default=0.0)
    
    # Métricas de permisos
    leaves_created = models.IntegerField(default=0)
    leaves_active = models.IntegerField(default=0)
    total_days_granted = models.IntegerField(default=0)
    
    # Métricas de conversaciones
    claude_conversations = models.IntegerField(default=0)
    avg_conversation_rating = models.FloatField(default=0.0)
    
    # Datos adicionales
    analytics_data = models.JSONField(
        default=dict,
        help_text='Datos adicionales de analytics'
    )
    
    class Meta:
        db_table = 'attendance_medical_analytics'
        ordering = ['-date']
        
    def __str__(self):
        return f"Analytics {self.date}"
