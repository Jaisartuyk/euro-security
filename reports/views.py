from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta, date
from employees.models import Employee
from departments.models import Department
from positions.models import Position
import json
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal


@login_required
def report_dashboard(request):
    """Vista principal del módulo de reportes"""
    
    # Estadísticas generales
    total_employees = Employee.objects.filter(is_active=True).count()
    total_departments = Department.objects.filter(is_active=True).count()
    total_positions = Position.objects.filter(is_active=True).count()
    
    # Empleados por mes (últimos 12 meses)
    today = timezone.now().date()
    twelve_months_ago = today - timedelta(days=365)
    
    context = {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'total_positions': total_positions,
    }
    
    return render(request, 'reports/dashboard.html', context)


@login_required
def employee_reports(request):
    """Vista para reportes de empleados"""
    
    # Filtros
    department_id = request.GET.get('department')
    position_id = request.GET.get('position')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    employees = Employee.objects.select_related('department', 'position').all()
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if position_id:
        employees = employees.filter(position_id=position_id)
    
    if date_from:
        employees = employees.filter(hire_date__gte=date_from)
    
    if date_to:
        employees = employees.filter(hire_date__lte=date_to)
    
    # Estadísticas
    stats = {
        'total': employees.count(),
        'active': employees.filter(is_active=True).count(),
        'inactive': employees.filter(is_active=False).count(),
        'avg_salary': employees.filter(is_active=True).aggregate(avg=Avg('current_salary'))['avg'] or 0,
        'total_payroll': employees.filter(is_active=True).aggregate(sum=Sum('current_salary'))['sum'] or 0,
    }
    
    # Datos para filtros
    departments = Department.objects.filter(is_active=True).order_by('name')
    positions = Position.objects.filter(is_active=True).order_by('title')
    
    context = {
        'employees': employees[:50],  # Limitar para rendimiento
        'stats': stats,
        'departments': departments,
        'positions': positions,
        'selected_department': department_id,
        'selected_position': position_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'reports/employee_reports.html', context)


@login_required
def department_reports(request):
    """Vista para reportes de departamentos"""
    
    departments = Department.objects.annotate(
        employee_count=Count('employees', filter=Q(employees__is_active=True)),
        total_payroll=Sum('employees__current_salary', filter=Q(employees__is_active=True)),
        avg_salary=Avg('employees__current_salary', filter=Q(employees__is_active=True))
    ).filter(is_active=True)
    
    # Estadísticas generales
    total_budget = departments.aggregate(sum=Sum('budget'))['sum'] or 0
    total_payroll = departments.aggregate(sum=Sum('total_payroll'))['sum'] or 0
    
    # Preparar datos JSON para los gráficos
    departments_json = []
    for dept in departments:
        departments_json.append({
            'name': dept.name,
            'employee_count': dept.employee_count or 0,
            'budget': float(dept.budget or 0),
            'total_payroll': float(dept.total_payroll or 0)
        })
    
    context = {
        'departments': departments,
        'departments_json': departments_json,
        'total_budget': total_budget,
        'total_payroll': total_payroll,
        'budget_utilization': (total_payroll / total_budget * 100) if total_budget > 0 else 0,
    }
    
    return render(request, 'reports/department_reports.html', context)


@login_required
def position_reports(request):
    """Vista para reportes de puestos"""
    
    positions = Position.objects.annotate(
        employee_count=Count('employees', filter=Q(employees__is_active=True)),
        avg_salary=Avg('employees__current_salary', filter=Q(employees__is_active=True))
    ).select_related('department').filter(is_active=True)
    
    # Estadísticas por nivel
    level_stats = Position.objects.filter(is_active=True).values(
        'level'
    ).annotate(
        count=Count('id'),
        employee_count=Count('employees', filter=Q(employees__is_active=True)),
        avg_min_salary=Avg('min_salary'),
        avg_max_salary=Avg('max_salary')
    ).order_by('-employee_count')
    
    context = {
        'positions': positions,
        'level_stats': level_stats,
    }
    
    return render(request, 'reports/position_reports.html', context)


@login_required
def payroll_reports(request):
    """Vista para reportes de nómina"""
    
    # Filtros
    department_id = request.GET.get('department')
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    employees = Employee.objects.filter(is_active=True).select_related('department', 'position')
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    # Cálculos de nómina
    payroll_data = []
    total_gross = 0
    
    for employee in employees:
        gross_salary = employee.current_salary
        # Cálculos básicos de deducciones (ejemplo) - convertir a Decimal para evitar errores
        tax_rate = Decimal('0.15')  # 15% impuestos
        social_rate = Decimal('0.0725')  # 7.25% seguro social
        
        tax_deduction = gross_salary * tax_rate
        social_security = gross_salary * social_rate
        total_deductions = tax_deduction + social_security
        net_salary = gross_salary - total_deductions
        
        payroll_data.append({
            'employee': employee,
            'gross_salary': gross_salary,
            'tax_deduction': tax_deduction,
            'social_security': social_security,
            'total_deductions': total_deductions,
            'net_salary': net_salary,
        })
        
        total_gross += gross_salary
    
    # Resumen de nómina
    total_tax = sum(item['tax_deduction'] for item in payroll_data)
    total_social_security = sum(item['social_security'] for item in payroll_data)
    total_deductions = sum(item['total_deductions'] for item in payroll_data)
    total_net = sum(item['net_salary'] for item in payroll_data)
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    
    # Preparar datos por departamento para gráficos
    department_payroll = []
    for dept in departments:
        dept_employees = [item for item in payroll_data if item['employee'].department == dept]
        dept_total = sum(item['gross_salary'] for item in dept_employees)
        if dept_total > 0:  # Solo incluir departamentos con nómina
            department_payroll.append({
                'name': dept.name,
                'total_payroll': float(dept_total)
            })
    
    # Preparar datos JSON para los gráficos
    payroll_json_data = {
        'total_net': float(total_net),
        'total_tax': float(total_tax),
        'total_social_security': float(total_social_security),
        'departments': department_payroll
    }
    
    context = {
        'payroll_data': payroll_data,
        'payroll_json_data': payroll_json_data,  # Datos JSON para gráficos
        'summary': {
            'total_gross': total_gross,
            'total_tax': total_tax,
            'total_social_security': total_social_security,
            'total_deductions': total_deductions,
            'total_net': total_net,
            'employee_count': len(payroll_data),
        },
        'departments': departments,
        'selected_department': department_id,
        'selected_month': month,
        'selected_year': year,
    }
    
    return render(request, 'reports/payroll_reports.html', context)


@login_required
def analytics_reports(request):
    """Vista para reportes analíticos y gráficos"""
    
    context = {
        'page_title': 'Reportes Analíticos'
    }
    
    return render(request, 'reports/analytics_reports.html', context)


@login_required
def reports_api(request):
    """API para obtener datos de reportes en formato JSON"""
    
    report_type = request.GET.get('type', 'general')
    
    if report_type == 'employees_by_department':
        data = list(Department.objects.annotate(
            employee_count=Count('employees', filter=Q(employees__is_active=True))
        ).values('name', 'employee_count'))
    
    elif report_type == 'employees_by_position':
        data = list(Position.objects.annotate(
            employee_count=Count('employees', filter=Q(employees__is_active=True))
        ).values('title', 'employee_count').order_by('-employee_count')[:10])
    
    elif report_type == 'salary_by_department':
        data = list(Department.objects.annotate(
            avg_salary=Avg('employees__current_salary', filter=Q(employees__is_active=True)),
            total_payroll=Sum('employees__current_salary', filter=Q(employees__is_active=True))
        ).values('name', 'avg_salary', 'total_payroll'))
    
    elif report_type == 'hiring_trends':
        # Empleados contratados por mes en el último año
        today = timezone.now().date()
        twelve_months_ago = today - timedelta(days=365)
        
        data = []
        for i in range(12):
            month_start = twelve_months_ago + timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            count = Employee.objects.filter(
                hire_date__gte=month_start,
                hire_date__lt=month_end
            ).count()
            
            data.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
    
    else:
        # Estadísticas generales
        data = {
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'total_departments': Department.objects.filter(is_active=True).count(),
            'total_positions': Position.objects.filter(is_active=True).count(),
            'avg_salary': Employee.objects.filter(is_active=True).aggregate(
                avg=Avg('current_salary')
            )['avg'] or 0,
        }
    
    return JsonResponse(data, safe=False, encoder=DjangoJSONEncoder)
