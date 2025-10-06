"""
Modelos para Sistema de Fotos de Seguridad con IA
"""

from django.db import models
from django.utils import timezone
from employees.models import Employee
from .models_gps import WorkArea
from .models import BaseModel


class SecurityPhoto(BaseModel):
    """Foto de seguridad con análisis de IA"""
    
    CAPTURE_TYPES = [
        ('AUTO', 'Automática'),
        ('MANUAL', 'Manual'),
        ('ATTENDANCE', 'Marcación'),
        ('ALERT', 'Alerta'),
        ('REQUEST', 'Solicitud Operaciones'),
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='security_photos'
    )
    
    # Foto
    photo = models.ImageField('Foto', upload_to='security_photos/%Y/%m/%d/')
    thumbnail = models.ImageField('Miniatura', upload_to='security_photos/thumbnails/%Y/%m/%d/', null=True, blank=True)
    
    # Ubicación
    latitude = models.DecimalField('Latitud', max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField('Longitud', max_digits=11, decimal_places=8, null=True, blank=True)
    work_area = models.ForeignKey(WorkArea, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField('Dirección', max_length=500, blank=True)
    
    # Metadatos
    capture_type = models.CharField('Tipo de Captura', max_length=20, choices=CAPTURE_TYPES, default='AUTO')
    timestamp = models.DateTimeField('Fecha y Hora', default=timezone.now)
    device_info = models.TextField('Info del Dispositivo', blank=True)
    
    # Análisis de IA
    ai_analyzed = models.BooleanField('Analizado por IA', default=False)
    ai_analysis_date = models.DateTimeField('Fecha Análisis IA', null=True, blank=True)
    ai_results = models.JSONField('Resultados IA', default=dict, blank=True)
    
    # Alertas
    has_alerts = models.BooleanField('Tiene Alertas', default=False)
    alert_level = models.CharField('Nivel de Alerta', max_length=20, choices=[
        ('NONE', 'Sin Alerta'),
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    ], default='NONE')
    
    class Meta:
        verbose_name = 'Foto de Seguridad'
        verbose_name_plural = 'Fotos de Seguridad'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', '-timestamp']),
            models.Index(fields=['work_area', '-timestamp']),
            models.Index(fields=['has_alerts', '-timestamp']),
            models.Index(fields=['ai_analyzed']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def analyze_with_ai(self):
        """Analizar foto con todos los servicios de IA"""
        from .ai_services import roboflow_service, facepp_service
        
        try:
            # Leer imagen
            with self.photo.open('rb') as f:
                image_bytes = f.read()
            
            results = {
                'weapons': [],
                'vehicles': [],
                'ppe': [],
                'persons': [],
                'face_attributes': None,
                'analyzed_at': timezone.now().isoformat()
            }
            
            # 1. Detectar armas
            weapons_result = roboflow_service.detect_weapons(image_bytes)
            if weapons_result.get('predictions'):
                results['weapons'] = weapons_result['predictions']
                if len(results['weapons']) > 0:
                    self.has_alerts = True
                    self.alert_level = 'CRITICAL'
            
            # 2. Detectar vehículos
            vehicles_result = roboflow_service.detect_vehicles(image_bytes)
            if vehicles_result.get('predictions'):
                results['vehicles'] = vehicles_result['predictions']
            
            # 3. Detectar EPP
            ppe_result = roboflow_service.detect_ppe(image_bytes)
            if ppe_result.get('predictions'):
                results['ppe'] = ppe_result['predictions']
                # Verificar si falta EPP
                for pred in results['ppe']:
                    if 'no-' in pred.get('class', '').lower():
                        self.has_alerts = True
                        if self.alert_level == 'NONE':
                            self.alert_level = 'MEDIUM'
            
            # 4. Detectar personas
            persons_result = roboflow_service.detect_persons(image_bytes)
            if persons_result.get('predictions'):
                results['persons'] = persons_result['predictions']
            
            # 5. Análisis facial
            face_attrs = facepp_service.analyze_face_attributes(image_bytes)
            if face_attrs:
                results['face_attributes'] = face_attrs
            
            # Guardar resultados
            self.ai_results = results
            self.ai_analyzed = True
            self.ai_analysis_date = timezone.now()
            self.save()
            
            # Crear alertas si es necesario
            if self.has_alerts:
                self.create_security_alert()
            
            return results
            
        except Exception as e:
            print(f"❌ Error analizando foto: {str(e)}")
            return None
    
    def create_security_alert(self):
        """Crear alerta de seguridad basada en análisis"""
        alert_messages = []
        
        if self.ai_results.get('weapons'):
            alert_messages.append(f"🔫 ARMA DETECTADA: {len(self.ai_results['weapons'])} objeto(s)")
        
        if self.ai_results.get('ppe'):
            for pred in self.ai_results['ppe']:
                if 'no-' in pred.get('class', '').lower():
                    alert_messages.append(f"⚠️ EPP FALTANTE: {pred.get('class')}")
        
        if alert_messages:
            SecurityAlert.objects.create(
                photo=self,
                employee=self.employee,
                alert_type='AI_DETECTION',
                severity=self.alert_level,
                message='\n'.join(alert_messages),
                ai_data=self.ai_results
            )
    
    def save(self, *args, **kwargs):
        """Crear thumbnail al guardar"""
        super().save(*args, **kwargs)
        
        # Crear thumbnail si no existe
        if self.photo and not self.thumbnail:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        """Crear miniatura de la foto"""
        try:
            from PIL import Image
            from io import BytesIO
            from django.core.files.uploadedfile import InMemoryUploadedFile
            import sys
            
            # Abrir imagen
            img = Image.open(self.photo)
            
            # Redimensionar
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Guardar en memoria
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)
            thumb_io.seek(0)
            
            # Crear archivo
            thumb_file = InMemoryUploadedFile(
                thumb_io, None, f'thumb_{self.photo.name}',
                'image/jpeg', sys.getsizeof(thumb_io), None
            )
            
            self.thumbnail.save(f'thumb_{self.photo.name}', thumb_file, save=True)
            
        except Exception as e:
            print(f"❌ Error creando thumbnail: {str(e)}")


class SecurityAlert(BaseModel):
    """Alerta de seguridad generada por IA"""
    
    ALERT_TYPES = [
        ('AI_DETECTION', 'Detección IA'),
        ('GEOFENCE', 'Geocerca'),
        ('PANIC', 'Botón de Pánico'),
        ('MANUAL', 'Manual'),
        ('BEHAVIOR', 'Comportamiento'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Baja'),
        ('MEDIUM', 'Media'),
        ('HIGH', 'Alta'),
        ('CRITICAL', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('ACKNOWLEDGED', 'Reconocida'),
        ('IN_PROGRESS', 'En Progreso'),
        ('RESOLVED', 'Resuelta'),
        ('FALSE_ALARM', 'Falsa Alarma'),
    ]
    
    photo = models.ForeignKey(SecurityPhoto, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='security_alerts')
    
    # Alerta
    alert_type = models.CharField('Tipo de Alerta', max_length=20, choices=ALERT_TYPES)
    severity = models.CharField('Severidad', max_length=20, choices=SEVERITY_LEVELS)
    message = models.TextField('Mensaje')
    ai_data = models.JSONField('Datos IA', default=dict, blank=True)
    
    # Estado
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='PENDING')
    acknowledged_by = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField('Reconocida en', null=True, blank=True)
    resolved_at = models.DateTimeField('Resuelta en', null=True, blank=True)
    resolution_notes = models.TextField('Notas de Resolución', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Alerta de Seguridad'
        verbose_name_plural = 'Alertas de Seguridad'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_severity_display()} - {self.employee.get_full_name()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def acknowledge(self, user):
        """Reconocer alerta"""
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_by = user.employee if hasattr(user, 'employee') else None
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self, notes=''):
        """Resolver alerta"""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()
    
    def mark_false_alarm(self, notes=''):
        """Marcar como falsa alarma"""
        self.status = 'FALSE_ALARM'
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()


class VideoSession(BaseModel):
    """Sesión de video en vivo"""
    
    STATUS_CHOICES = [
        ('REQUESTED', 'Solicitado'),
        ('ACTIVE', 'Activo'),
        ('ENDED', 'Finalizado'),
        ('REJECTED', 'Rechazado'),
        ('TIMEOUT', 'Tiempo Agotado'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='video_sessions')
    requester = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requested_videos')
    
    # Agora
    channel_name = models.CharField('Canal', max_length=100, unique=True)
    employee_token = models.TextField('Token Empleado')
    requester_token = models.TextField('Token Solicitante')
    
    # Estado
    status = models.CharField('Estado', max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    started_at = models.DateTimeField('Iniciado', null=True, blank=True)
    ended_at = models.DateTimeField('Finalizado', null=True, blank=True)
    duration_seconds = models.IntegerField('Duración (seg)', default=0)
    
    # Grabación
    recording_url = models.URLField('URL Grabación', blank=True)
    
    class Meta:
        verbose_name = 'Sesión de Video'
        verbose_name_plural = 'Sesiones de Video'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_status_display()}"
    
    def start(self):
        """Iniciar sesión"""
        self.status = 'ACTIVE'
        self.started_at = timezone.now()
        self.save()
    
    def end(self):
        """Finalizar sesión"""
        self.status = 'ENDED'
        self.ended_at = timezone.now()
        if self.started_at:
            duration = (self.ended_at - self.started_at).total_seconds()
            self.duration_seconds = int(duration)
        self.save()
