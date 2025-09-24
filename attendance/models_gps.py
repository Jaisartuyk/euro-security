"""
Modelos para el sistema de rastreo GPS en tiempo real
EURO SECURITY - GPS Tracking Models
"""
from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee
from core.models import BaseModel
from django.utils import timezone
import math

class WorkArea(BaseModel):
    """Áreas de trabajo definidas geográficamente"""
    
    AREA_TYPES = [
        ('OFFICE', 'Oficina'),
        ('BUILDING', 'Edificio'),
        ('MALL', 'Centro Comercial'),
        ('RESIDENTIAL', 'Residencial'),
        ('INDUSTRIAL', 'Industrial'),
        ('PATROL', 'Ronda/Patrullaje'),
        ('EVENT', 'Evento'),
        ('OTHER', 'Otro'),
    ]
    
    name = models.CharField('Nombre del Área', max_length=200)
    description = models.TextField('Descripción', blank=True)
    area_type = models.CharField('Tipo de Área', max_length=20, choices=AREA_TYPES)
    
    # Coordenadas del centro del área
    latitude = models.DecimalField('Latitud', max_digits=10, decimal_places=8)
    longitude = models.DecimalField('Longitud', max_digits=11, decimal_places=8)
    
    # Radio de cobertura en metros
    radius_meters = models.IntegerField('Radio de Cobertura (metros)', default=50)
    
    # Información adicional
    address = models.TextField('Dirección', blank=True)
    contact_person = models.CharField('Persona de Contacto', max_length=200, blank=True)
    contact_phone = models.CharField('Teléfono de Contacto', max_length=20, blank=True)
    
    # Configuración de horarios
    start_time = models.TimeField('Hora de Inicio', null=True, blank=True)
    end_time = models.TimeField('Hora de Fin', null=True, blank=True)
    
    # Estado
    is_active = models.BooleanField('Activa', default=True)
    requires_attendance = models.BooleanField('Requiere Marcación', default=True)
    
    class Meta:
        verbose_name = 'Área de Trabajo'
        verbose_name_plural = 'Áreas de Trabajo'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_area_type_display()})"
    
    def is_within_area(self, lat, lng, tolerance_meters=0):
        """Verifica si una coordenada está dentro del área"""
        distance = self.calculate_distance(lat, lng)
        allowed_radius = self.radius_meters + tolerance_meters
        return distance <= allowed_radius
    
    def calculate_distance(self, lat, lng):
        """Calcula la distancia en metros desde el centro del área"""
        # Fórmula de Haversine para calcular distancia entre dos puntos GPS
        R = 6371000  # Radio de la Tierra en metros
        
        lat1 = math.radians(float(self.latitude))
        lon1 = math.radians(float(self.longitude))
        lat2 = math.radians(float(lat))
        lon2 = math.radians(float(lng))
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

class EmployeeWorkArea(BaseModel):
    """Asignación de empleados a áreas de trabajo"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_areas')
    work_area = models.ForeignKey(WorkArea, on_delete=models.CASCADE, related_name='assigned_employees')
    
    # Configuración específica del empleado
    is_primary = models.BooleanField('Área Principal', default=False)
    tolerance_meters = models.IntegerField('Tolerancia Extra (metros)', default=0)
    
    # Horarios específicos (opcional, sobrescribe los del área)
    custom_start_time = models.TimeField('Hora de Inicio Personalizada', null=True, blank=True)
    custom_end_time = models.TimeField('Hora de Fin Personalizada', null=True, blank=True)
    
    # Días de la semana (1=Lunes, 7=Domingo)
    monday = models.BooleanField('Lunes', default=True)
    tuesday = models.BooleanField('Martes', default=True)
    wednesday = models.BooleanField('Miércoles', default=True)
    thursday = models.BooleanField('Jueves', default=True)
    friday = models.BooleanField('Viernes', default=True)
    saturday = models.BooleanField('Sábado', default=False)
    sunday = models.BooleanField('Domingo', default=False)
    
    # Estado
    is_active = models.BooleanField('Activa', default=True)
    assigned_date = models.DateField('Fecha de Asignación', default=timezone.now)
    
    class Meta:
        verbose_name = 'Asignación de Área'
        verbose_name_plural = 'Asignaciones de Áreas'
        unique_together = ['employee', 'work_area']
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.work_area.name}"
    
    def is_work_day_today(self):
        """Verifica si hoy es día laboral para esta asignación"""
        today = timezone.now().weekday() + 1  # 1=Lunes, 7=Domingo
        days = {
            1: self.monday, 2: self.tuesday, 3: self.wednesday,
            4: self.thursday, 5: self.friday, 6: self.saturday, 7: self.sunday
        }
        return days.get(today, False)

class GPSTracking(BaseModel):
    """Registro de ubicaciones GPS en tiempo real"""
    
    TRACKING_TYPES = [
        ('AUTO', 'Automático'),
        ('MANUAL', 'Manual'),
        ('ATTENDANCE', 'Marcación'),
        ('PATROL', 'Patrullaje'),
        ('EMERGENCY', 'Emergencia'),
        ('SUPERUSER', 'Superusuario'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='gps_tracking', null=True, blank=True)
    
    # Ubicación GPS
    latitude = models.DecimalField('Latitud', max_digits=10, decimal_places=8)
    longitude = models.DecimalField('Longitud', max_digits=11, decimal_places=8)
    accuracy = models.FloatField('Precisión GPS (metros)', null=True, blank=True)
    altitude = models.FloatField('Altitud (metros)', null=True, blank=True)
    
    # Información del tracking
    tracking_type = models.CharField('Tipo de Rastreo', max_length=20, choices=TRACKING_TYPES, default='AUTO')
    timestamp = models.DateTimeField('Fecha y Hora', default=timezone.now)
    
    # Área de trabajo relacionada (si aplica)
    work_area = models.ForeignKey(WorkArea, on_delete=models.SET_NULL, null=True, blank=True)
    is_within_work_area = models.BooleanField('Dentro del Área', default=False)
    distance_to_work_area = models.FloatField('Distancia al Área (metros)', null=True, blank=True)
    
    # Información adicional
    battery_level = models.IntegerField('Nivel de Batería (%)', null=True, blank=True)
    device_info = models.TextField('Información del Dispositivo', blank=True)
    notes = models.TextField('Notas', blank=True)
    
    # Estado
    is_active_session = models.BooleanField('Sesión Activa', default=True)
    
    class Meta:
        verbose_name = 'Rastreo GPS'
        verbose_name_plural = 'Rastreos GPS'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', '-timestamp']),
            models.Index(fields=['work_area', '-timestamp']),
            models.Index(fields=['is_active_session', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Verificar automáticamente si está dentro del área de trabajo"""
        if not self.work_area:
            # Buscar el área de trabajo más cercana del empleado
            employee_areas = EmployeeWorkArea.objects.filter(
                employee=self.employee,
                is_active=True
            ).select_related('work_area')
            
            closest_area = None
            min_distance = float('inf')
            
            for emp_area in employee_areas:
                distance = emp_area.work_area.calculate_distance(self.latitude, self.longitude)
                if distance < min_distance:
                    min_distance = distance
                    closest_area = emp_area.work_area
            
            if closest_area:
                self.work_area = closest_area
                self.distance_to_work_area = min_distance
                self.is_within_work_area = closest_area.is_within_area(
                    self.latitude, 
                    self.longitude,
                    tolerance_meters=employee_areas.filter(work_area=closest_area).first().tolerance_meters
                )
        
        super().save(*args, **kwargs)

class LocationAlert(BaseModel):
    """Alertas de ubicación"""
    
    ALERT_TYPES = [
        ('OUT_OF_AREA', 'Fuera del Área'),
        ('LATE_ARRIVAL', 'Llegada Tarde'),
        ('EARLY_DEPARTURE', 'Salida Temprana'),
        ('NO_MOVEMENT', 'Sin Movimiento'),
        ('EMERGENCY', 'Emergencia'),
        ('BATTERY_LOW', 'Batería Baja'),
    ]
    
    ALERT_LEVELS = [
        ('INFO', 'Información'),
        ('WARNING', 'Advertencia'),
        ('CRITICAL', 'Crítica'),
        ('EMERGENCY', 'Emergencia'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='location_alerts')
    work_area = models.ForeignKey(WorkArea, on_delete=models.CASCADE, null=True, blank=True)
    gps_tracking = models.ForeignKey(GPSTracking, on_delete=models.CASCADE, null=True, blank=True)
    
    alert_type = models.CharField('Tipo de Alerta', max_length=20, choices=ALERT_TYPES)
    alert_level = models.CharField('Nivel de Alerta', max_length=20, choices=ALERT_LEVELS, default='WARNING')
    
    title = models.CharField('Título', max_length=200)
    message = models.TextField('Mensaje')
    
    # Estado
    is_resolved = models.BooleanField('Resuelta', default=False)
    resolved_at = models.DateTimeField('Resuelta el', null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Notificaciones
    notified_supervisors = models.ManyToManyField(User, related_name='received_alerts', blank=True)
    
    class Meta:
        verbose_name = 'Alerta de Ubicación'
        verbose_name_plural = 'Alertas de Ubicación'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.employee.get_full_name()}"
