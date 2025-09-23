from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Position
from .forms import PositionForm, PositionFilterForm
from departments.models import Department


@login_required
def position_list(request):
    """Vista para listar todos los puestos de trabajo"""
    positions = Position.objects.select_related('department').all()
    
    # Filtros
    search = request.GET.get('search')
    department_id = request.GET.get('department')
    level = request.GET.get('level')
    employment_type = request.GET.get('employment_type')
    status = request.GET.get('status')
    hiring = request.GET.get('hiring')
    
    if search:
        positions = positions.filter(
            Q(title__icontains=search) | 
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    if department_id:
        positions = positions.filter(department_id=department_id)
    
    if level:
        positions = positions.filter(level=level)
    
    if employment_type:
        positions = positions.filter(employment_type=employment_type)
    
    if status:
        is_active = status == 'active'
        positions = positions.filter(is_active=is_active)
    
    if hiring:
        is_hiring = hiring == 'yes'
        positions = positions.filter(is_hiring=is_hiring)
    
    # Agregar conteo de empleados actuales
    positions = positions.annotate(
        current_employees=Count('employees', filter=Q(employees__is_active=True))
    )
    
    # Ordenamiento
    positions = positions.order_by('department__name', 'title')
    
    # Paginación
    paginator = Paginator(positions, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    departments = Department.objects.filter(is_active=True).order_by('name')
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'position_levels': Position.POSITION_LEVELS,
        'employment_types': Position.EMPLOYMENT_TYPES,
        'search': search,
        'selected_department': department_id,
        'selected_level': level,
        'selected_employment_type': employment_type,
        'selected_status': status,
        'selected_hiring': hiring,
    }
    
    return render(request, 'positions/position_list.html', context)


@login_required
def position_create(request):
    """Vista para crear un nuevo puesto de trabajo"""
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            messages.success(request, f'Puesto "{position.title}" creado exitosamente.')
            return redirect('positions:detail', pk=position.pk)
    else:
        form = PositionForm()
    
    return render(request, 'positions/position_form.html', {
        'form': form,
        'title': 'Crear Puesto de Trabajo'
    })


@login_required
def position_detail(request, pk):
    """Vista para ver detalles de un puesto de trabajo"""
    position = get_object_or_404(Position.objects.select_related('department'), pk=pk)
    
    # Obtener empleados actuales en este puesto
    current_employees = position.employees.filter(is_active=True).select_related('department')[:10]
    total_employees = position.employees.filter(is_active=True).count()
    
    # Calcular estadísticas
    available_positions = position.get_available_positions()
    avg_salary = position.employees.filter(is_active=True).aggregate(
        avg=Avg('current_salary')
    )['avg'] or 0
    
    context = {
        'position': position,
        'current_employees': current_employees,
        'total_employees': total_employees,
        'available_positions': available_positions,
        'avg_salary': avg_salary,
    }
    
    return render(request, 'positions/position_detail.html', context)


@login_required
def position_edit(request, pk):
    """Vista para editar un puesto de trabajo"""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save()
            messages.success(request, f'Puesto "{position.title}" actualizado exitosamente.')
            return redirect('positions:detail', pk=position.pk)
    else:
        form = PositionForm(instance=position)
    
    return render(request, 'positions/position_form.html', {
        'form': form,
        'position': position,
        'title': 'Editar Puesto de Trabajo'
    })


@login_required
def position_stats_api(request):
    """API para obtener estadísticas de puestos de trabajo"""
    from django.db.models import Count, Sum, Avg
    
    stats = Position.objects.aggregate(
        total_positions=Count('id'),
        active_positions=Count('id', filter=Q(is_active=True)),
        hiring_positions=Count('id', filter=Q(is_hiring=True, is_active=True)),
        avg_min_salary=Avg('min_salary', filter=Q(is_active=True)),
        avg_max_salary=Avg('max_salary', filter=Q(is_active=True))
    )
    
    # Estadísticas por nivel
    level_stats = Position.objects.filter(is_active=True).values(
        'level'
    ).annotate(
        count=Count('id'),
        avg_min_salary=Avg('min_salary'),
        avg_max_salary=Avg('max_salary')
    ).order_by('-count')
    
    # Estadísticas por departamento
    dept_stats = Position.objects.filter(is_active=True).values(
        'department__name'
    ).annotate(
        count=Count('id'),
        avg_salary=Avg('min_salary')
    ).order_by('-count')[:5]
    
    return JsonResponse({
        'general_stats': stats,
        'level_stats': list(level_stats),
        'department_stats': list(dept_stats)
    })
