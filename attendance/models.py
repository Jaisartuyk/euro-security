"""
Modelos para el sistema de asistencia con reconocimiento facial
"""
from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta
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


# ============================================================================
# MODELOS PARA SISTEMA DE TURNOS Y HORARIOS
# ============================================================================

class ShiftTemplate(models.Model):
    """
    Plantillas de turnos predefinidas para facilitar la configuración
    """
    
    SHIFT_TYPES = [
        ('FIXED', 'Turno Fijo'),
        ('ROTATING', 'Turno Rotativo'),
        ('FLEXIBLE', 'Horario Flexible'),
        ('SPLIT', 'Turno Dividido'),
    ]
    
    TEMPLATE_CATEGORIES = [
        ('STANDARD', 'Estándar (8 horas)'),
        ('EXTENDED', 'Extendido (12 horas)'),
        ('SECURITY', 'Seguridad (24/7)'),
        ('OFFICE', 'Oficina'),
        ('CUSTOM', 'Personalizado'),
    ]
    
    name = models.CharField('Nombre de la Plantilla', max_length=100)
    description = models.TextField('Descripción', blank=True)
    category = models.CharField('Categoría', max_length=20, choices=TEMPLATE_CATEGORIES)
    shift_type = models.CharField('Tipo de Turno', max_length=20, choices=SHIFT_TYPES)
    
    # Configuración de turnos
    total_shifts_per_day = models.PositiveIntegerField('Turnos por Día', default=3)
    hours_per_shift = models.DecimalField('Horas por Turno', max_digits=4, decimal_places=2, default=8.0)
    
    # Configuración de rotación (si aplica)
    rotation_days = models.PositiveIntegerField('Días de Rotación', default=7, 
                                               help_text="Cada cuántos días rota el turno")
    
    # Configuración visual
    icon_name = models.CharField('Icono', max_length=50, default='fas fa-clock',
                                help_text="Clase CSS del icono FontAwesome")
    color_primary = models.CharField('Color Primario', max_length=7, default='#3b82f6')
    color_secondary = models.CharField('Color Secundario', max_length=7, default='#1e40af')
    
    # Configuración JSON para turnos específicos
    shifts_config = models.TextField('Configuración de Turnos', default='[]',
                                   help_text="JSON con configuración detallada de cada turno")
    
    # Metadatos
    is_active = models.BooleanField('Activo', default=True)
    is_default = models.BooleanField('Plantilla por Defecto', default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Plantilla de Turno'
        verbose_name_plural = 'Plantillas de Turnos'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def get_shifts_config_list(self):
        """Retorna la configuración de turnos como lista de Python"""
        try:
            return json.loads(self.shifts_config)
        except json.JSONDecodeError:
            return []
    
    def save(self, *args, **kwargs):
        # Solo una plantilla puede ser default por categoría
        if self.is_default:
            ShiftTemplate.objects.filter(
                category=self.category, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class WorkSchedule(models.Model):
    """
    Horarios de trabajo para empleados o departamentos
    """
    
    SCHEDULE_TYPES = [
        ('INDIVIDUAL', 'Individual'),
        ('DEPARTMENT', 'Por Departamento'),
        ('POSITION', 'Por Puesto'),
        ('GLOBAL', 'Global'),
    ]
    
    name = models.CharField('Nombre del Horario', max_length=100)
    description = models.TextField('Descripción', blank=True)
    schedule_type = models.CharField('Tipo de Horario', max_length=20, choices=SCHEDULE_TYPES)
    
    # Relación con plantilla
    shift_template = models.ForeignKey(ShiftTemplate, on_delete=models.CASCADE, 
                                     related_name='work_schedules',
                                     verbose_name='Plantilla de Turno')
    
    # Fechas de vigencia
    start_date = models.DateField('Fecha de Inicio')
    end_date = models.DateField('Fecha de Fin', null=True, blank=True,
                               help_text="Dejar vacío para horario indefinido")
    
    # Configuración de horas extras
    overtime_threshold_daily = models.DecimalField('Umbral Diario Horas Extras', 
                                                  max_digits=4, decimal_places=2, default=8.0)
    overtime_threshold_weekly = models.DecimalField('Umbral Semanal Horas Extras', 
                                                   max_digits=4, decimal_places=2, default=40.0)
    
    # Configuración de horas nocturnas
    night_shift_start = models.TimeField('Inicio Turno Nocturno', default=time(22, 0))
    night_shift_end = models.TimeField('Fin Turno Nocturno', default=time(6, 0))
    night_shift_multiplier = models.DecimalField('Multiplicador Nocturno', 
                                                max_digits=3, decimal_places=2, default=1.25)
    
    # Configuración de descansos
    break_duration_minutes = models.PositiveIntegerField('Duración Descanso (min)', default=60)
    paid_break_minutes = models.PositiveIntegerField('Descanso Pagado (min)', default=15)
    
    # Estado
    is_active = models.BooleanField('Activo', default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Horario de Trabajo'
        verbose_name_plural = 'Horarios de Trabajo'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.shift_template.name}"
    
    def is_night_time(self, check_time):
        """Verifica si una hora específica está en turno nocturno"""
        if isinstance(check_time, datetime):
            check_time = check_time.time()
        
        if self.night_shift_start <= self.night_shift_end:
            # Turno nocturno no cruza medianoche
            return self.night_shift_start <= check_time <= self.night_shift_end
        else:
            # Turno nocturno cruza medianoche
            return check_time >= self.night_shift_start or check_time <= self.night_shift_end


class Shift(models.Model):
    """
    Turnos específicos dentro de un horario de trabajo
    """
    
    SHIFT_NAMES = [
        ('MORNING', 'Matutino'),
        ('AFTERNOON', 'Vespertino'),
        ('NIGHT', 'Nocturno'),
        ('DAWN', 'Madrugada'),
        ('CUSTOM', 'Personalizado'),
    ]
    
    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.CASCADE, 
                                    related_name='shifts', verbose_name='Horario de Trabajo')
    
    name = models.CharField('Nombre del Turno', max_length=20, choices=SHIFT_NAMES)
    custom_name = models.CharField('Nombre Personalizado', max_length=50, blank=True)
    
    # Horarios
    start_time = models.TimeField('Hora de Inicio')
    end_time = models.TimeField('Hora de Fin')
    
    # Configuración
    is_overnight = models.BooleanField('Turno Nocturno', default=False,
                                     help_text="Marca si el turno cruza medianoche")
    break_start_time = models.TimeField('Inicio de Descanso', null=True, blank=True)
    break_end_time = models.TimeField('Fin de Descanso', null=True, blank=True)
    
    # Tolerancias
    late_tolerance_minutes = models.PositiveIntegerField('Tolerancia Llegada Tarde (min)', default=15)
    early_exit_tolerance_minutes = models.PositiveIntegerField('Tolerancia Salida Temprana (min)', default=15)
    
    # Configuración visual
    color = models.CharField('Color del Turno', max_length=7, default='#3b82f6')
    icon = models.CharField('Icono', max_length=50, default='fas fa-sun')
    
    # Estado
    is_active = models.BooleanField('Activo', default=True)
    order = models.PositiveIntegerField('Orden', default=1)
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['work_schedule', 'order', 'start_time']
        unique_together = ['work_schedule', 'order']
    
    def __str__(self):
        name = self.custom_name if self.custom_name else self.get_name_display()
        return f"{name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
    
    def get_duration_hours(self):
        """Calcula la duración del turno en horas"""
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        
        if self.is_overnight:
            end_datetime += timedelta(days=1)
        
        duration = end_datetime - start_datetime
        return duration.total_seconds() / 3600
    
    def clean(self):
        """Validaciones del modelo"""
        if self.start_time == self.end_time:
            raise ValidationError("La hora de inicio no puede ser igual a la hora de fin")
        
        if not self.is_overnight and self.start_time > self.end_time:
            raise ValidationError("Para turnos que no cruzan medianoche, la hora de inicio debe ser menor a la de fin")


class EmployeeShiftAssignment(models.Model):
    """
    Asignación de empleados a turnos específicos
    """
    
    ASSIGNMENT_STATUS = [
        ('ACTIVE', 'Activo'),
        ('PENDING', 'Pendiente'),
        ('COMPLETED', 'Completado'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, 
                               related_name='shift_assignments', verbose_name='Empleado')
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, 
                            related_name='employee_assignments', verbose_name='Turno')
    
    # Fechas de asignación
    start_date = models.DateField('Fecha de Inicio')
    end_date = models.DateField('Fecha de Fin', null=True, blank=True)
    
    # Configuración de rotación
    rotation_pattern = models.TextField('Patrón de Rotación', blank=True,
                                      help_text="JSON con patrón de rotación específico")
    
    # Estado
    status = models.CharField('Estado', max_length=20, choices=ASSIGNMENT_STATUS, default='ACTIVE')
    is_primary_shift = models.BooleanField('Turno Principal', default=True)
    
    # Metadatos
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Asignado por')
    notes = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Asignación de Turno'
        verbose_name_plural = 'Asignaciones de Turnos'
        ordering = ['-created_at']
        unique_together = ['employee', 'shift', 'start_date']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.shift} ({self.start_date})"
    
    def get_rotation_pattern_list(self):
        """Retorna el patrón de rotación como lista de Python"""
        try:
            return json.loads(self.rotation_pattern) if self.rotation_pattern else []
        except json.JSONDecodeError:
            return []
    
    def is_active_on_date(self, check_date):
        """Verifica si la asignación está activa en una fecha específica"""
        if check_date < self.start_date:
            return False
        if self.end_date and check_date > self.end_date:
            return False
        return self.status == 'ACTIVE'
