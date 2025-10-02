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
# MODELOS PARA SISTEMA DE TURNOS Y HORARIOS - EURO SECURITY
# Actualizado: 2025-09-26 - Sistema profesional de gestión de turnos
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
    
    SHIFT_CATEGORIES = [
        ('GENERAL', 'General'),
        ('CARGA_NACIONAL', 'Carga Nacional'),
        ('CARGA_INTERNACIONAL', 'Carga Internacional'),
    ]
    
    name = models.CharField('Nombre de la Plantilla', max_length=100)
    description = models.TextField('Descripción', blank=True)
    category = models.CharField('Categoría', max_length=20, choices=TEMPLATE_CATEGORIES)
    shift_type = models.CharField('Tipo de Turno', max_length=20, choices=SHIFT_TYPES)
    
    # ✅ CAMPOS ACTIVADOS - Migración 0009 aplicada exitosamente en Railway
    shift_code = models.CharField(
        'Código de Turno', 
        max_length=5, 
        blank=True, 
        null=True,
        help_text='Código específico del cliente (D, C, S, A, Y, etc.)'
    )
    shift_category = models.CharField(
        'Categoría de Turno',
        max_length=20,
        choices=SHIFT_CATEGORIES,
        default='GENERAL'
    )
    is_split_shift = models.BooleanField(
        'Turno Dividido',
        default=False,
        help_text='Turno con descanso largo en el medio'
    )
    split_break_start = models.TimeField(
        'Inicio Descanso Split',
        null=True,
        blank=True,
        help_text='Hora de inicio del descanso largo'
    )
    split_break_end = models.TimeField(
        'Fin Descanso Split',
        null=True,
        blank=True,
        help_text='Hora de fin del descanso largo'
    )
    max_agents = models.PositiveIntegerField(
        'Máximo Agentes',
        default=999,
        help_text='Máximo número de agentes para este turno'
    )
    weekday_schedule = models.JSONField(
        'Horario por Día de Semana',
        default=dict,
        blank=True,
        help_text='Horarios específicos por día: {1: "05:45-17:45", 6: "05:30-17:30"}'
    )
    is_variable_schedule = models.BooleanField(
        'Horario Variable',
        default=False,
        help_text='Turno con horario variable según itinerario (TAMPA)'
    )
    
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
    
    def get_schedule_for_day(self, weekday):
        """
        Retorna horario específico según día de la semana
        weekday: 1=Lunes, 7=Domingo
        """
        try:
            if (hasattr(self, 'weekday_schedule') and self.weekday_schedule and 
                str(weekday) in self.weekday_schedule):
                schedule_str = self.weekday_schedule[str(weekday)]
                if '-' in schedule_str:
                    start, end = schedule_str.split('-')
                    return {'start': start.strip(), 'end': end.strip()}
        except AttributeError:
            pass
        
        # Retornar horario por defecto de la configuración
        shifts_config = self.get_shifts_config_list()
        if shifts_config:
            first_shift = shifts_config[0]
            return {
                'start': first_shift.get('start_time', '08:00'),
                'end': first_shift.get('end_time', '17:00')
            }
        
        return {'start': '08:00', 'end': '17:00'}
    
    def get_display_name(self):
        """Retorna nombre para mostrar con código si existe"""
        try:
            if hasattr(self, 'shift_code') and self.shift_code:
                return f"{self.shift_code} - {self.name}"
        except AttributeError:
            pass
        return self.name
    
    def get_total_hours(self):
        """Calcula horas totales considerando turnos divididos"""
        try:
            if (hasattr(self, 'is_split_shift') and self.is_split_shift and 
                hasattr(self, 'split_break_start') and self.split_break_start and
                hasattr(self, 'split_break_end') and self.split_break_end):
                shifts_config = self.get_shifts_config_list()
                total_minutes = 0
                
                for shift in shifts_config:
                    start_time = datetime.strptime(shift.get('start_time', '08:00'), '%H:%M').time()
                    end_time = datetime.strptime(shift.get('end_time', '17:00'), '%H:%M').time()
                    
                    # Calcular duración del segmento
                    start_datetime = datetime.combine(datetime.today(), start_time)
                    end_datetime = datetime.combine(datetime.today(), end_time)
                    
                    if end_time < start_time:  # Cruza medianoche
                        end_datetime += timedelta(days=1)
                    
                    duration = end_datetime - start_datetime
                    total_minutes += duration.total_seconds() / 60
                
                return total_minutes / 60
        except AttributeError:
            pass
        
        return float(self.hours_per_shift)
    
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
    
    class Meta:
        db_table = 'attendance_employeeshiftassignment'
        unique_together = ['employee', 'shift', 'start_date']


# =============================================================================
# MODELOS MÉDICOS CON DR. CLAUDE IA
# =============================================================================

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


# =============================================================================
# SISTEMA DE GESTIÓN DE AUSENCIAS Y PERMISOS LABORALES
# =============================================================================

class LeaveType(models.TextChoices):
    """Tipos de ausencias laborales"""
    # Médicas (manejadas por Dr. Claude IA)
    MEDICAL_DISABILITY = 'medical_disability', 'Incapacidad Médica'
    MEDICAL_APPOINTMENT = 'medical_appointment', 'Cita Médica'
    MEDICAL_EMERGENCY = 'medical_emergency', 'Emergencia Médica'
    
    # Personales
    DOMESTIC_CALAMITY = 'domestic_calamity', 'Calamidad Doméstica'
    PERSONAL_MATTER = 'personal_matter', 'Asunto Personal'
    PERSONAL_ERRAND = 'personal_errand', 'Diligencia Personal'
    MARRIAGE_PERMIT = 'marriage_permit', 'Permiso Matrimonio'
    BEREAVEMENT = 'bereavement', 'Duelo Familiar'
    
    # Educativas
    STUDY_PERMIT = 'study_permit', 'Permiso Estudio'
    ACADEMIC_EXAM = 'academic_exam', 'Examen Académico'
    TRAINING = 'training', 'Capacitación'
    
    # Legales
    COURT_SUMMONS = 'court_summons', 'Citación Judicial'
    LEGAL_PROCEDURE = 'legal_procedure', 'Trámite Legal'
    MANDATORY_APPEARANCE = 'mandatory_appearance', 'Comparecencia Obligatoria'
    
    # Otros
    PAID_LEAVE = 'paid_leave', 'Permiso Remunerado'
    COMPENSATORY_DAY = 'compensatory_day', 'Día Compensatorio'
    SPECIAL_LICENSE = 'special_license', 'Licencia Especial'
    UNPAID_LEAVE = 'unpaid_leave', 'Licencia No Remunerada'
    VACATION = 'vacation', 'Vacaciones'


class LeaveStatus(models.TextChoices):
    """Estados del proceso de aprobación"""
    DRAFT = 'draft', 'Borrador'
    PENDING_SUPERVISOR = 'pending_supervisor', 'Pendiente Jefe'
    APPROVED_SUPERVISOR = 'approved_supervisor', 'Aprobado por Jefe'
    REJECTED_SUPERVISOR = 'rejected_supervisor', 'Rechazado por Jefe'
    PENDING_HR = 'pending_hr', 'Pendiente RRHH'
    APPROVED_HR = 'approved_hr', 'Aprobado por RRHH'
    REJECTED_HR = 'rejected_hr', 'Rechazado por RRHH'
    ACTIVE = 'active', 'Activo'
    COMPLETED = 'completed', 'Completado'
    CANCELLED = 'cancelled', 'Cancelado'


class LeaveRequest(models.Model):
    """
    Solicitud de Ausencia Laboral - Sistema completo de permisos
    Integra con Dr. Claude IA para permisos médicos
    """
    
    PERMISSION_MODE_CHOICES = [
        ('DAYS', 'Por Días'),
        ('HOURS', 'Por Horas'),
    ]
    
    # =========================================================================
    # DATOS DEL EMPLEADO SOLICITANTE
    # =========================================================================
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name='Empleado'
    )
    employee_code = models.CharField(
        'Código Empleado',
        max_length=20,
        blank=True
    )
    project = models.CharField(
        'Proyecto',
        max_length=100,
        blank=True,
        help_text='Proyecto o cliente asignado'
    )
    area = models.ForeignKey(
        'departments.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Área/Departamento'
    )
    immediate_supervisor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_leave_requests',
        verbose_name='Jefe Inmediato'
    )
    
    # =========================================================================
    # TIPO DE PERMISO
    # =========================================================================
    leave_type = models.CharField(
        'Tipo de Ausencia',
        max_length=30,
        choices=LeaveType.choices
    )
    permission_mode = models.CharField(
        'Modo de Permiso',
        max_length=10,
        choices=PERMISSION_MODE_CHOICES,
        default='DAYS'
    )
    
    # =========================================================================
    # DURACIÓN DEL PERMISO - POR DÍAS
    # =========================================================================
    start_date = models.DateField(
        'Fecha Desde',
        null=True,
        blank=True
    )
    end_date = models.DateField(
        'Fecha Hasta',
        null=True,
        blank=True
    )
    total_days = models.IntegerField(
        'Total Días',
        default=0
    )
    
    # =========================================================================
    # DURACIÓN DEL PERMISO - POR HORAS
    # =========================================================================
    permission_date = models.DateField(
        'Fecha del Permiso',
        null=True,
        blank=True,
        help_text='Para permisos por horas'
    )
    start_time = models.TimeField(
        'Hora Desde',
        null=True,
        blank=True
    )
    end_time = models.TimeField(
        'Hora Hasta',
        null=True,
        blank=True
    )
    total_hours = models.DecimalField(
        'Total Horas',
        max_digits=5,
        decimal_places=2,
        default=0
    )
    
    # =========================================================================
    # JUSTIFICACIÓN Y DOCUMENTOS
    # =========================================================================
    reason_description = models.TextField(
        'Descripción del Motivo',
        help_text='Explique brevemente el motivo de la ausencia'
    )
    supporting_document = models.FileField(
        'Documento de Soporte',
        upload_to='leave_requests/%Y/%m/',
        null=True,
        blank=True,
        help_text='Certificado, constancia, etc.'
    )
    
    # =========================================================================
    # INTEGRACIÓN CON DR. CLAUDE IA (Solo para ausencias médicas)
    # =========================================================================
    medical_leave = models.ForeignKey(
        MedicalLeave,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leave_request',
        verbose_name='Permiso Médico IA',
        help_text='Vinculado si fue generado por Dr. Claude'
    )
    ai_generated = models.BooleanField(
        'Generado por IA',
        default=False,
        help_text='Si Dr. Claude auto-llenó este formulario'
    )
    ai_confidence = models.FloatField(
        'Confianza IA',
        default=0.0,
        help_text='Nivel de confianza de Dr. Claude (0.0 - 1.0)'
    )
    ai_recommendation = models.CharField(
        'Recomendación IA',
        max_length=100,
        blank=True,
        help_text='Recomendación de Dr. Claude'
    )
    
    # =========================================================================
    # ESTADO Y FLUJO DE APROBACIÓN
    # =========================================================================
    status = models.CharField(
        'Estado',
        max_length=30,
        choices=LeaveStatus.choices,
        default=LeaveStatus.DRAFT
    )
    
    # =========================================================================
    # FIRMAS DIGITALES Y FECHAS
    # =========================================================================
    employee_signature_date = models.DateTimeField(
        'Fecha Firma Empleado',
        null=True,
        blank=True
    )
    supervisor_signature_date = models.DateTimeField(
        'Fecha Firma Jefe',
        null=True,
        blank=True
    )
    hr_signature_date = models.DateTimeField(
        'Fecha Firma RRHH',
        null=True,
        blank=True
    )
    
    # =========================================================================
    # REVISIÓN Y COMENTARIOS
    # =========================================================================
    supervisor_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervisor_reviewed_leaves',
        verbose_name='Revisado por Jefe'
    )
    supervisor_comments = models.TextField(
        'Comentarios del Jefe',
        blank=True
    )
    supervisor_decision_date = models.DateTimeField(
        'Fecha Decisión Jefe',
        null=True,
        blank=True
    )
    
    hr_reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_reviewed_leaves',
        verbose_name='Revisado por RRHH'
    )
    hr_comments = models.TextField(
        'Comentarios de RRHH',
        blank=True
    )
    hr_decision_date = models.DateTimeField(
        'Fecha Decisión RRHH',
        null=True,
        blank=True
    )
    
    # =========================================================================
    # IMPACTO EN TURNOS Y ASISTENCIA
    # =========================================================================
    affects_shifts = models.BooleanField(
        'Afecta Turnos',
        default=True,
        help_text='Si esta ausencia afecta turnos asignados'
    )
    shifts_affected = models.JSONField(
        'Turnos Afectados',
        default=list,
        help_text='IDs de turnos afectados'
    )
    requires_coverage = models.BooleanField(
        'Requiere Reemplazo',
        default=False,
        help_text='Si se necesita cubrir el turno'
    )
    replacement_employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replacement_leaves',
        verbose_name='Empleado Reemplazo'
    )
    
    # =========================================================================
    # METADATOS
    # =========================================================================
    request_number = models.CharField(
        'Número de Solicitud',
        max_length=20,
        unique=True,
        blank=True,
        help_text='Código único de la solicitud'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(
        'Fecha de Envío',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Solicitud de Ausencia'
        verbose_name_plural = 'Solicitudes de Ausencia'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['leave_type', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.request_number or 'SIN-NUM'} - {self.employee.get_full_name()} - {self.get_leave_type_display()}"
    
    def save(self, *args, **kwargs):
        # Generar número de solicitud único
        if not self.request_number:
            today = timezone.now()
            prefix = f"AUS-{today.year}-"
            last_request = LeaveRequest.objects.filter(
                request_number__startswith=prefix
            ).order_by('-request_number').first()
            
            if last_request:
                try:
                    last_num = int(last_request.request_number.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
            
            self.request_number = f"{prefix}{new_num:05d}"
        
        # Auto-llenar código de empleado
        if not self.employee_code and self.employee:
            self.employee_code = self.employee.employee_id
        
        # Calcular total de días o horas
        if self.permission_mode == 'DAYS' and self.start_date and self.end_date:
            self.total_days = (self.end_date - self.start_date).days + 1
        elif self.permission_mode == 'HOURS' and self.start_time and self.end_time:
            start_dt = datetime.combine(datetime.today(), self.start_time)
            end_dt = datetime.combine(datetime.today(), self.end_time)
            duration = end_dt - start_dt
            self.total_hours = duration.total_seconds() / 3600
        
        super().save(*args, **kwargs)
    
    def is_medical_leave(self):
        """Verifica si es una ausencia médica"""
        medical_types = [
            LeaveType.MEDICAL_DISABILITY,
            LeaveType.MEDICAL_APPOINTMENT,
            LeaveType.MEDICAL_EMERGENCY,
        ]
        return self.leave_type in medical_types
    
    def requires_supervisor_approval(self):
        """Verifica si requiere aprobación del jefe"""
        # Citaciones judiciales van directo a RRHH
        if self.leave_type == LeaveType.COURT_SUMMONS:
            return False
        # Todo lo demás requiere aprobación del jefe
        return True
    
    def can_auto_approve(self):
        """Verifica si puede ser auto-aprobado por IA"""
        return self.is_medical_leave() and self.ai_confidence >= 0.85
    
    def submit(self):
        """Enviar solicitud para aprobación"""
        self.submitted_at = timezone.now()
        self.employee_signature_date = timezone.now()
        
        if self.can_auto_approve():
            self.status = LeaveStatus.APPROVED_SUPERVISOR
            self.supervisor_comments = "Auto-aprobado por Dr. Claude IA"
            self.supervisor_signature_date = timezone.now()
        elif not self.requires_supervisor_approval():
            self.status = LeaveStatus.PENDING_HR
        else:
            self.status = LeaveStatus.PENDING_SUPERVISOR
        
        self.save()
    
    def approve_by_supervisor(self, user, comments=""):
        """Aprobar por jefe inmediato"""
        self.status = LeaveStatus.APPROVED_SUPERVISOR
        self.supervisor_reviewed_by = user
        self.supervisor_comments = comments
        self.supervisor_decision_date = timezone.now()
        self.supervisor_signature_date = timezone.now()
        # Pasa a RRHH
        self.status = LeaveStatus.PENDING_HR
        self.save()
    
    def reject_by_supervisor(self, user, comments=""):
        """Rechazar por jefe inmediato"""
        self.status = LeaveStatus.REJECTED_SUPERVISOR
        self.supervisor_reviewed_by = user
        self.supervisor_comments = comments
        self.supervisor_decision_date = timezone.now()
        self.save()
    
    def approve_by_hr(self, user, comments=""):
        """Aprobar por RRHH - Aprobación final"""
        self.status = LeaveStatus.APPROVED_HR
        self.hr_reviewed_by = user
        self.hr_comments = comments
        self.hr_decision_date = timezone.now()
        self.hr_signature_date = timezone.now()
        
        # Si las fechas ya pasaron o están en curso, marcar como activo
        today = timezone.now().date()
        if self.permission_mode == 'DAYS':
            if self.start_date <= today <= self.end_date:
                self.status = LeaveStatus.ACTIVE
            elif self.end_date < today:
                self.status = LeaveStatus.COMPLETED
        
        self.save()
    
    def reject_by_hr(self, user, comments=""):
        """Rechazar por RRHH"""
        self.status = LeaveStatus.REJECTED_HR
        self.hr_reviewed_by = user
        self.hr_comments = comments
        self.hr_decision_date = timezone.now()
        self.save()
    
    def cancel(self):
        """Cancelar solicitud"""
        self.status = LeaveStatus.CANCELLED
        self.save()
    
    def get_status_color(self):
        """Color para el badge de estado"""
        colors = {
            LeaveStatus.DRAFT: 'secondary',
            LeaveStatus.PENDING_SUPERVISOR: 'warning',
            LeaveStatus.APPROVED_SUPERVISOR: 'info',
            LeaveStatus.REJECTED_SUPERVISOR: 'danger',
            LeaveStatus.PENDING_HR: 'warning',
            LeaveStatus.APPROVED_HR: 'success',
            LeaveStatus.REJECTED_HR: 'danger',
            LeaveStatus.ACTIVE: 'primary',
            LeaveStatus.COMPLETED: 'secondary',
            LeaveStatus.CANCELLED: 'dark',
        }
        return colors.get(self.status, 'secondary')
    
    def get_approval_level(self):
        """Nivel actual de aprobación"""
        if self.status in [LeaveStatus.DRAFT, LeaveStatus.PENDING_SUPERVISOR]:
            return 1  # Pendiente jefe
        elif self.status in [LeaveStatus.APPROVED_SUPERVISOR, LeaveStatus.PENDING_HR]:
            return 2  # Pendiente RRHH
        elif self.status in [LeaveStatus.APPROVED_HR, LeaveStatus.ACTIVE, LeaveStatus.COMPLETED]:
            return 3  # Aprobado final
        else:
            return 0  # Rechazado/Cancelado
        """Verifica si la asignación está activa en una fecha específica"""
        if check_date < self.start_date:
            return False
        if self.end_date and check_date > self.end_date:
            return False
        return self.status == 'ACTIVE'
