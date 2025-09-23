from django.db import models
from core.models import BaseModel


class Report(BaseModel):
    """Modelo para reportes del sistema"""
    
    REPORT_TYPES = [
        ('EMPLOYEE', 'Reporte de Empleados'),
        ('DEPARTMENT', 'Reporte de Departamentos'),
        ('SALARY', 'Reporte Salarial'),
        ('CUSTOM', 'Reporte Personalizado'),
    ]
    
    name = models.CharField('Nombre del Reporte', max_length=200)
    report_type = models.CharField('Tipo de Reporte', max_length=20, choices=REPORT_TYPES)
    description = models.TextField('Descripción', blank=True)
    is_active = models.BooleanField('Activo', default=True)
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['name']
    
    def __str__(self):
        return self.name
