from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel


class Department(BaseModel):
    """Modelo para los departamentos de la empresa"""
    
    DEPARTMENT_TYPES = [
        ('RRHH', 'Recursos Humanos'),
        ('SISTEMAS', 'Sistemas'),
        ('MARKETING', 'Marketing y Comunicaciones'),
        ('DIGITAL', 'Transformación Digital'),
        ('OPERACIONES', 'Operaciones'),
        ('ADMINISTRACION', 'Administración'),
        ('SEGURIDAD', 'Seguridad Física'),
        ('FINANZAS', 'Finanzas'),
        ('LOGISTICA', 'Logística'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('COMERCIAL', 'Comercial y Ventas'),
    ]
    
    name = models.CharField('Nombre', max_length=100)
    code = models.CharField('Código', max_length=10, unique=True)
    department_type = models.CharField('Tipo de Departamento', max_length=20, choices=DEPARTMENT_TYPES)
    description = models.TextField('Descripción', blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               verbose_name='Jefe de Departamento')
    budget = models.DecimalField('Presupuesto', max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField('Activo', default=True)
    
    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_employee_count(self):
        """Retorna el número de empleados en el departamento"""
        return self.employees.filter(is_active=True).count()
    
    def get_positions_count(self):
        """Retorna el número de puestos en el departamento"""
        return self.positions.filter(is_active=True).count()


class DepartmentBudget(BaseModel):
    """Modelo para el control de presupuesto por departamento"""
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, 
                                 related_name='budget_records')
    year = models.IntegerField('Año')
    month = models.IntegerField('Mes')
    allocated_budget = models.DecimalField('Presupuesto Asignado', max_digits=12, decimal_places=2)
    spent_budget = models.DecimalField('Presupuesto Gastado', max_digits=12, decimal_places=2, default=0)
    notes = models.TextField('Notas', blank=True)
    
    class Meta:
        verbose_name = 'Presupuesto Departamental'
        verbose_name_plural = 'Presupuestos Departamentales'
        unique_together = ['department', 'year', 'month']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.department.name} - {self.month}/{self.year}"
    
    @property
    def remaining_budget(self):
        """Calcula el presupuesto restante"""
        return self.allocated_budget - self.spent_budget
    
    @property
    def budget_utilization_percentage(self):
        """Calcula el porcentaje de utilización del presupuesto"""
        if self.allocated_budget > 0:
            return (self.spent_budget / self.allocated_budget) * 100
        return 0
