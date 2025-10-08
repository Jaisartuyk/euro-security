"""
Vistas para el Sistema de Control de Calidad y Gestión de Riesgos
Dashboard profesional con gráficos y matriz interactiva
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import json
from .models import RiskCategory, Risk, ControlMeasure, RiskAssessment, RiskIncident
from employees.models import Employee
from departments.models import Department


def user_has_quality_access(user):
    """Verifica si el usuario tiene acceso al módulo de Control de Calidad"""
    if user.is_superuser or user.is_staff:
        return True
    
    # Verificar si el usuario es empleado del departamento de Control de Calidad
    try:
        employee = Employee.objects.get(user=user)
        
        # Excepción: Jefa de Operaciones tiene acceso
        if employee.employee_id == 'EMP13807414':
            return True
        
        # Empleados del departamento de Control de Calidad
        if employee.department and employee.department.code == 'CC':
            return True
    except Employee.DoesNotExist:
        pass
    
    return False


@login_required
def quality_dashboard(request):
    """Dashboard principal de Control de Calidad"""
    
    # Verificar permisos
    if not user_has_quality_access(request.user):
        messages.error(request, 'No tienes permisos para acceder al módulo de Control de Calidad.')
        return redirect('dashboard:home')
    
    # Estadísticas generales
    total_risks = Risk.objects.filter(is_active=True).count()
    high_risks = Risk.objects.filter(is_active=True, risk_level='ALTO').count()
    medium_risks = Risk.objects.filter(is_active=True, risk_level='MEDIO').count()
    low_risks = Risk.objects.filter(is_active=True, risk_level='BAJO').count()
    mitigated_risks = Risk.objects.filter(is_mitigated=True).count()
    
    # Medidas de control
    total_measures = ControlMeasure.objects.count()
    pending_measures = ControlMeasure.objects.filter(status='PENDIENTE').count()
    in_progress_measures = ControlMeasure.objects.filter(status='EN_PROGRESO').count()
    completed_measures = ControlMeasure.objects.filter(status='COMPLETADA').count()
    overdue_measures = ControlMeasure.objects.filter(
        status__in=['PENDIENTE', 'EN_PROGRESO'],
        due_date__lt=timezone.now().date()
    ).count()
    
    # Incidentes
    total_incidents = RiskIncident.objects.count()
    unresolved_incidents = RiskIncident.objects.filter(is_resolved=False).count()
    critical_incidents = RiskIncident.objects.filter(
        severity='CRITICO',
        is_resolved=False
    ).count()
    
    # Riesgos por categoría
    risks_by_category = RiskCategory.objects.annotate(
        risk_count=Count('risks', filter=Q(risks__is_active=True))
    ).order_by('-risk_count')
    
    # Riesgos de alto nivel (Top 10)
    top_risks = Risk.objects.filter(is_active=True).order_by('-risk_score')[:10]
    
    # Medidas próximas a vencer (próximos 7 días)
    upcoming_due = ControlMeasure.objects.filter(
        status__in=['PENDIENTE', 'EN_PROGRESO'],
        due_date__gte=timezone.now().date(),
        due_date__lte=timezone.now().date() + timedelta(days=7)
    ).order_by('due_date')[:5]
    
    # Incidentes recientes
    recent_incidents = RiskIncident.objects.order_by('-incident_date')[:5]
    
    # Datos para gráficos (convertir a JSON)
    # Riesgos por nivel (para gráfico de dona)
    risk_levels_data = json.dumps({
        'labels': ['Alto', 'Medio', 'Bajo'],
        'data': [high_risks, medium_risks, low_risks],
        'colors': ['#dc3545', '#ffc107', '#28a745']
    })
    
    # Riesgos por categoría (para gráfico de barras)
    category_labels = json.dumps([cat.name for cat in risks_by_category])
    category_data = json.dumps([cat.risk_count for cat in risks_by_category])
    category_colors = json.dumps([cat.color for cat in risks_by_category])
    
    # Medidas por estado (para gráfico de dona)
    measures_status_data = json.dumps({
        'labels': ['Pendiente', 'En Progreso', 'Completada'],
        'data': [pending_measures, in_progress_measures, completed_measures],
        'colors': ['#6c757d', '#007bff', '#28a745']
    })
    
    context = {
        # Estadísticas
        'total_risks': total_risks,
        'high_risks': high_risks,
        'medium_risks': medium_risks,
        'low_risks': low_risks,
        'mitigated_risks': mitigated_risks,
        'total_measures': total_measures,
        'pending_measures': pending_measures,
        'in_progress_measures': in_progress_measures,
        'completed_measures': completed_measures,
        'overdue_measures': overdue_measures,
        'total_incidents': total_incidents,
        'unresolved_incidents': unresolved_incidents,
        'critical_incidents': critical_incidents,
        
        # Datos
        'risks_by_category': risks_by_category,
        'top_risks': top_risks,
        'upcoming_due': upcoming_due,
        'recent_incidents': recent_incidents,
        
        # Gráficos
        'risk_levels_data': risk_levels_data,
        'category_labels': category_labels,
        'category_data': category_data,
        'category_colors': category_colors,
        'measures_status_data': measures_status_data,
    }
    
    return render(request, 'quality_control/dashboard.html', context)


@login_required
def risk_matrix(request):
    """Matriz de riesgos interactiva"""
    
    if not user_has_quality_access(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard:home')
    
    # Obtener todos los riesgos activos
    risks = Risk.objects.filter(is_active=True).select_related('category', 'responsible')
    
    # Organizar riesgos en matriz 5x5
    matrix = {}
    for i in range(1, 6):
        matrix[i] = {}
        for j in range(1, 6):
            matrix[i][j] = []
    
    for risk in risks:
        matrix[risk.probability][risk.impact].append(risk)
    
    context = {
        'matrix': matrix,
        'risks': risks,
    }
    
    return render(request, 'quality_control/risk_matrix.html', context)


@login_required
def risk_list(request):
    """Lista de riesgos con filtros"""
    
    if not user_has_quality_access(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard:home')
    
    # Filtros
    category_filter = request.GET.get('category', '')
    level_filter = request.GET.get('level', '')
    status_filter = request.GET.get('status', 'active')
    
    risks = Risk.objects.select_related('category', 'responsible', 'department')
    
    if category_filter:
        risks = risks.filter(category_id=category_filter)
    
    if level_filter:
        risks = risks.filter(risk_level=level_filter)
    
    if status_filter == 'active':
        risks = risks.filter(is_active=True)
    elif status_filter == 'mitigated':
        risks = risks.filter(is_mitigated=True)
    elif status_filter == 'all':
        pass
    
    risks = risks.order_by('-risk_score', 'title')
    
    categories = RiskCategory.objects.filter(is_active=True)
    
    context = {
        'risks': risks,
        'categories': categories,
        'category_filter': category_filter,
        'level_filter': level_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'quality_control/risk_list.html', context)


@login_required
def risk_detail(request, risk_id):
    """Detalle de un riesgo específico"""
    
    if not user_has_quality_access(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard:home')
    
    risk = get_object_or_404(Risk, id=risk_id)
    
    # Medidas de control del riesgo
    control_measures = risk.control_measures.all().order_by('-priority', 'due_date')
    
    # Evaluaciones históricas
    assessments = risk.assessments.all().order_by('-assessment_date')[:10]
    
    # Incidentes relacionados
    incidents = risk.incidents.all().order_by('-incident_date')[:10]
    
    context = {
        'risk': risk,
        'control_measures': control_measures,
        'assessments': assessments,
        'incidents': incidents,
    }
    
    return render(request, 'quality_control/risk_detail.html', context)


@login_required
def control_measures_list(request):
    """Lista de medidas de control"""
    
    if not user_has_quality_access(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard:home')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    measures = ControlMeasure.objects.select_related('risk', 'responsible')
    
    if status_filter:
        measures = measures.filter(status=status_filter)
    
    if priority_filter:
        measures = measures.filter(priority=priority_filter)
    
    measures = measures.order_by('-priority', 'due_date')
    
    context = {
        'measures': measures,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
    }
    
    return render(request, 'quality_control/control_measures.html', context)


@login_required
def incidents_list(request):
    """Lista de incidentes"""
    
    if not user_has_quality_access(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard:home')
    
    # Filtros
    severity_filter = request.GET.get('severity', '')
    status_filter = request.GET.get('status', 'unresolved')
    
    incidents = RiskIncident.objects.select_related('risk', 'reported_by')
    
    if severity_filter:
        incidents = incidents.filter(severity=severity_filter)
    
    if status_filter == 'unresolved':
        incidents = incidents.filter(is_resolved=False)
    elif status_filter == 'resolved':
        incidents = incidents.filter(is_resolved=True)
    
    incidents = incidents.order_by('-incident_date')
    
    context = {
        'incidents': incidents,
        'severity_filter': severity_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'quality_control/incidents.html', context)


@login_required
def reports(request):
    """Reportes y estadísticas"""
    
    if not user_has_quality_access(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('dashboard:home')
    
    # Aquí se agregarán reportes personalizados
    context = {}
    
    return render(request, 'quality_control/reports.html', context)
