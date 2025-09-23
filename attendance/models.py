"""
Modelos para el sistema de asistencia con reconocimiento facial
"""
from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from django.utils import timezone
import json
from .models_gps import WorkArea, EmployeeWorkArea, GPSTracking, LocationAlert


class AttendanceRecord(models.Model):
    """Registro de asistencia de empleados"""
    
    ATTENDANCE_TYPES = [
        ('IN', 'Entrada'),
        ('OUT', 'Salida'),
        ('BREAK_OUT', 'Salida a Descanso'),
        ('BREAK_IN', 'Regreso de Descanso'),
    ]
    
    VERIFICATION_METHODS = [
        ('FACIAL', 'Reconocimiento Facial'),
        ('MANUAL', 'Manual por Supervisor'),
        ('EMERGENCY', 'Emergencia'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    attendance_type = models.CharField(max_length=10, choices=ATTENDANCE_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    verification_method = models.CharField(max_length=10, choices=VERIFICATION_METHODS, default='FACIAL')
    
    # Datos de geolocalización
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    location_accuracy = models.FloatField(null=True, blank=True, help_text="Precisión en metros")
    address = models.TextField(blank=True, help_text="Dirección obtenida por geocodificación inversa")
    
    # Datos biométricos
    facial_confidence = models.FloatField(null=True, blank=True, help_text="Confianza del reconocimiento facial (0-1)")
    facial_image_path = models.CharField(max_length=500, blank=True, help_text="Ruta de la imagen capturada")
    
    # Metadatos
    device_info = models.TextField(blank=True, help_text="Información del dispositivo usado")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Notas adicionales")
    
    # Control de validación
    is_valid = models.BooleanField(default=True, help_text="Si el registro es válido")
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='validated_attendances')
    validation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Registro de Asistencia"
        verbose_name_plural = "Registros de Asistencia"
        indexes = [
            models.Index(fields=['employee', 'timestamp']),
            models.Index(fields=['attendance_type', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.get_attendance_type_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
    
    def get_location_display(self):
        """Retorna la ubicación en formato legible"""
        if self.latitude and self.longitude:
            return f"{self.latitude}, {self.longitude}"
        return "Ubicación no disponible"
    
    def is_within_work_location(self, tolerance_meters=100):
        """Verifica si la marcación está dentro del área de trabajo permitida"""
        # Coordenadas de ejemplo de EURO SECURITY (se pueden configurar)
        WORK_LOCATIONS = [
            {'name': 'Oficina Principal', 'lat': 19.4326, 'lng': -99.1332, 'radius': 50},
            {'name': 'Sucursal Norte', 'lat': 19.4969, 'lng': -99.1276, 'radius': 30},
        ]
        
        if not self.latitude or not self.longitude:
            return False
            
        from math import radians, cos, sin, asin, sqrt
        
        def haversine(lon1, lat1, lon2, lat2):
            """Calcula la distancia entre dos puntos en la Tierra"""
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371000  # Radio de la Tierra en metros
            return c * r
        
        for location in WORK_LOCATIONS:
            distance = haversine(float(self.longitude), float(self.latitude), 
                               location['lng'], location['lat'])
            if distance <= location['radius']:
                return True
        
        return False


class AttendanceSummary(models.Model):
    """Resumen diario de asistencia por empleado"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_summaries')
    date = models.DateField()
    
    # Horarios
    first_entry = models.DateTimeField(null=True, blank=True)
    last_exit = models.DateTimeField(null=True, blank=True)
    total_work_hours = models.DurationField(null=True, blank=True)
    total_break_time = models.DurationField(null=True, blank=True)
    
    # Contadores
    entries_count = models.PositiveIntegerField(default=0)
    exits_count = models.PositiveIntegerField(default=0)
    break_count = models.PositiveIntegerField(default=0)
    
    # Estado del día
    is_present = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    is_early_exit = models.BooleanField(default=False)
    
    # Ubicaciones visitadas
    locations_visited = models.TextField(blank=True, help_text="JSON con ubicaciones visitadas")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee__last_name']
        verbose_name = "Resumen de Asistencia"
        verbose_name_plural = "Resúmenes de Asistencia"
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.date.strftime('%d/%m/%Y')}"
    
    def get_work_hours_display(self):
        """Retorna las horas trabajadas en formato legible"""
        if self.total_work_hours:
            total_seconds = int(self.total_work_hours.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return "0h 0m"
    
    def get_locations_list(self):
        """Retorna la lista de ubicaciones visitadas"""
        if self.locations_visited:
            try:
                return json.loads(self.locations_visited)
            except json.JSONDecodeError:
                return []
        return []


class FacialRecognitionProfile(models.Model):
    """Perfil de reconocimiento facial del empleado"""
    
    employee = models.OneToOneField(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='facial_profile'
    )
    face_encoding = models.TextField(
        blank=True,
        help_text="Codificación facial serializada en base64"
    )
    confidence_threshold = models.FloatField(
        default=0.75,
        help_text="Umbral de confianza para reconocimiento (0.0-1.0)"
    )
    reference_images = models.TextField(
        blank=True,
        help_text="Metadatos de imágenes de referencia"
    )
    
    # Campos para subida de imágenes
    image_1 = models.ImageField(
        upload_to='facial_profiles/',
        blank=True,
        null=True,
        help_text="Primera imagen de referencia"
    )
    image_2 = models.ImageField(
        upload_to='facial_profiles/',
        blank=True,
        null=True,
        help_text="Segunda imagen de referencia"
    )
    image_3 = models.ImageField(
        upload_to='facial_profiles/',
        blank=True,
        null=True,
        help_text="Tercera imagen de referencia"
    )
    image_4 = models.ImageField(
        upload_to='facial_profiles/',
        blank=True,
        null=True,
        help_text="Cuarta imagen de referencia (opcional)"
    )
    image_5 = models.ImageField(
        upload_to='facial_profiles/',
        blank=True,
        null=True,
        help_text="Quinta imagen de referencia (opcional)"
    )
    # Estadísticas
    total_recognitions = models.PositiveIntegerField(default=0)
    successful_recognitions = models.PositiveIntegerField(default=0)
    last_recognition = models.DateTimeField(null=True, blank=True)
    
    # Control
    is_active = models.BooleanField(default=True)
    needs_retraining = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Reconocimiento Facial"
        verbose_name_plural = "Perfiles de Reconocimiento Facial"
    
    def __str__(self):
        return f"Perfil Facial - {self.employee.get_full_name()}"
    
    def get_success_rate(self):
        """Calcula la tasa de éxito del reconocimiento"""
        if self.total_recognitions == 0:
            return 0.0
        return (self.successful_recognitions / self.total_recognitions) * 100
    
    def process_uploaded_images(self):
        """Procesa las imágenes subidas y genera codificación facial"""
        from .facial_recognition import facial_recognition_system
        from PIL import Image
        import json
        import base64
        
        images = [self.image_1, self.image_2, self.image_3, self.image_4, self.image_5]
        valid_images = [img for img in images if img and img.name]
        
        if len(valid_images) < 2:
            return False, "Se requieren al menos 2 imágenes"
        
        try:
            all_features = []
            processed_count = 0
            
            for image_field in valid_images:
                try:
                    # Abrir imagen
                    pil_image = Image.open(image_field.path)
                    
                    # Extraer características
                    features, location, quality = facial_recognition_system.extract_face_encoding(pil_image)
                    
                    if features and quality > 0.3:  # Calidad mínima
                        all_features.append(features)
                        processed_count += 1
                    
                except Exception as e:
                    print(f"Error procesando imagen {image_field.name}: {str(e)}")
                    continue
            
            if processed_count < 2:
                return False, "No se pudieron procesar suficientes imágenes válidas"
            
            # Crear codificación promedio
            if all_features:
                # Combinar todas las características
                combined_features = self._combine_features(all_features)
                
                # Codificar en base64
                features_json = json.dumps(combined_features)
                self.face_encoding = base64.b64encode(features_json.encode('utf-8')).decode('utf-8')
                self.reference_images = str(processed_count)
                self.save()
                
                return True, f"Perfil creado con {processed_count} imágenes"
            
            return False, "No se pudieron extraer características faciales"
            
        except Exception as e:
            return False, f"Error procesando imágenes: {str(e)}"
    
    def _combine_features(self, features_list):
        """Combina múltiples conjuntos de características en uno promedio"""
        import numpy as np
        
        if not features_list:
            return {}
        
        # Inicializar resultado
        combined = {
            'histogram': [],
            'lbp': [],
            'edges': 0,
            'hu_moments': [],
            'color': [],
            'gradient_mean': []
        }
        
        # Promediar cada tipo de característica
        for key in combined.keys():
            values = []
            for features in features_list:
                if key in features and features[key] is not None:
                    if isinstance(features[key], list):
                        values.extend([features[key]])
                    else:
                        values.append(features[key])
            
            if values:
                if isinstance(values[0], list):
                    # Promediar listas
                    combined[key] = np.mean(values, axis=0).tolist()
                else:
                    # Promediar valores escalares
                    combined[key] = np.mean(values)
        
        return combined
    
    def get_reference_images_list(self):
        """Retorna la lista de imágenes de referencia"""
        if self.reference_images:
            try:
                return json.loads(self.reference_images)
            except json.JSONDecodeError:
                return []
        return []


class AttendanceSettings(models.Model):
    """Configuraciones del sistema de asistencia"""
    
    # Horarios de trabajo
    work_start_time = models.TimeField(default="08:00:00")
    work_end_time = models.TimeField(default="17:00:00")
    break_duration_minutes = models.PositiveIntegerField(default=60)
    
    # Tolerancias
    late_tolerance_minutes = models.PositiveIntegerField(default=15)
    early_exit_tolerance_minutes = models.PositiveIntegerField(default=15)
    location_tolerance_meters = models.PositiveIntegerField(default=100)
    
    # Reconocimiento facial
    facial_confidence_threshold = models.FloatField(default=0.6)
    max_recognition_attempts = models.PositiveIntegerField(default=3)
    
    # Ubicaciones de trabajo (JSON)
    work_locations = models.TextField(default='[]', help_text="JSON con ubicaciones de trabajo permitidas")
    
    # Control
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Asistencia"
        verbose_name_plural = "Configuraciones de Asistencia"
    
    def __str__(self):
        return f"Configuración de Asistencia - {self.created_at.strftime('%d/%m/%Y')}"
    
    def get_work_locations_list(self):
        """Retorna la lista de ubicaciones de trabajo"""
        try:
            return json.loads(self.work_locations)
        except json.JSONDecodeError:
            return []
