from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.permissions import get_employee_from_user
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from employees.models import Employee
from departments.models import Department
from positions.models import Position


@login_required
def dashboard_home(request):
    """Vista principal del dashboard"""
    
    # Verificar si el usuario es un empleado (no admin)
    employee = get_employee_from_user(request.user)
    if employee and not request.user.is_superuser:
        # Redirigir empleados a su dashboard personalizado
        return redirect('employees:dashboard')
    
    # Solo administradores y superusuarios ven el dashboard administrativo
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect('login')
    
    # Obtener fecha actual y del mes
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    
    # Estadísticas básicas
    total_employees = Employee.objects.filter(is_active=True).count()
    total_departments = Department.objects.filter(is_active=True).count()
    total_positions = Position.objects.filter(is_active=True).count()
    new_employees_this_month = Employee.objects.filter(
        hire_date__gte=first_day_month,
        is_active=True
    ).count()
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_positions': total_positions,
        'new_employees_this_month': new_employees_this_month,
    }
    
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_stats_api(request):
    """API para obtener estadísticas del dashboard"""
    
    # Estadísticas generales
    general_stats = {
        'total_employees': Employee.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_positions': Position.objects.filter(is_active=True).count(),
        'avg_salary': Employee.objects.filter(is_active=True).aggregate(
            avg=Avg('current_salary')
        )['avg'] or 0,
    }
    
    # Estadísticas por departamento
    dept_stats = Department.objects.filter(is_active=True).annotate(
        employee_count=Count('employees', filter=Q(employees__is_active=True))
    ).values('name', 'employee_count').order_by('-employee_count')[:5]
    
    # Estadísticas por género
    gender_stats = Employee.objects.filter(is_active=True).values('gender').annotate(
        count=Count('id')
    )
    
    return JsonResponse({
        'general_stats': general_stats,
        'department_stats': list(dept_stats),
        'gender_stats': list(gender_stats)
    })
