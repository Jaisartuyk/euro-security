from django.db import models
from core.models import BaseModel


class Position(BaseModel):
    """Modelo para los puestos de trabajo"""
    
    POSITION_LEVELS = [
        ('ENTRY', 'Nivel de Entrada'),
        ('JUNIOR', 'Junior'),
        ('SENIOR', 'Senior'),
        ('LEAD', 'Líder'),
        ('MANAGER', 'Gerente'),
        ('DIRECTOR', 'Director'),
    ]
    
    EMPLOYMENT_TYPES = [
        ('FULL_TIME', 'Tiempo Completo'),
        ('PART_TIME', 'Medio Tiempo'),
        ('CONTRACT', 'Contrato'),
        ('TEMPORARY', 'Temporal'),
    ]
    
    title = models.CharField('Título del Puesto', max_length=100)
    code = models.CharField('Código', max_length=15, unique=True)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE, 
                                 related_name='positions', verbose_name='Departamento')
    description = models.TextField('Descripción del Puesto')
    
    # Información salarial
    min_salary = models.DecimalField('Salario Mínimo', max_digits=10, decimal_places=2)
    max_salary = models.DecimalField('Salario Máximo', max_digits=10, decimal_places=2)
    
    # Clasificación
    level = models.CharField('Nivel', max_length=20, choices=POSITION_LEVELS)
    employment_type = models.CharField('Tipo de Empleo', max_length=20, choices=EMPLOYMENT_TYPES)
    
    # Configuración
    max_positions = models.PositiveIntegerField('Máximo de Puestos', default=1)
    
    # Estado
    is_active = models.BooleanField('Activo', default=True)
    is_hiring = models.BooleanField('En Proceso de Contratación', default=False)
    
    class Meta:
        verbose_name = 'Puesto de Trabajo'
        verbose_name_plural = 'Puestos de Trabajo'
        ordering = ['department__name', 'title']
    
    def __str__(self):
        return f"{self.code} - {self.title}"
    
    def get_current_employees_count(self):
        """Retorna el número actual de empleados en este puesto"""
        return self.employees.filter(is_active=True).count()
    
    def get_available_positions(self):
        """Retorna el número de posiciones disponibles"""
        return self.max_positions - self.get_current_employees_count()
    
    @property
    def salary_range(self):
        """Retorna el rango salarial formateado"""
        return f"${self.min_salary:,.2f} - ${self.max_salary:,.2f}"
