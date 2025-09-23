from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Department, DepartmentBudget
from .forms import DepartmentForm, DepartmentBudgetForm


@login_required
def department_list(request):
    """Vista para listar todos los departamentos"""
    departments = Department.objects.all()
    
    # Filtros
    search = request.GET.get('search')
    department_type = request.GET.get('type')
    status = request.GET.get('status')
    
    if search:
        departments = departments.filter(
            Q(name__icontains=search) | 
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )
    
    if department_type:
        departments = departments.filter(department_type=department_type)
    
    if status:
        is_active = status == 'active'
        departments = departments.filter(is_active=is_active)
    
    # Paginación
    paginator = Paginator(departments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'department_types': Department.DEPARTMENT_TYPES,
        'search': search,
        'selected_type': department_type,
        'selected_status': status,
    }
    
    return render(request, 'departments/department_list.html', context)


@login_required
def department_create(request):
    """Vista para crear un nuevo departamento"""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Departamento "{department.name}" creado exitosamente.')
            return redirect('departments:detail', pk=department.pk)
    else:
        form = DepartmentForm()
    
    return render(request, 'departments/department_form.html', {
        'form': form,
        'title': 'Crear Departamento'
    })


@login_required
def department_detail(request, pk):
    """Vista para ver detalles de un departamento"""
    department = get_object_or_404(Department, pk=pk)
    
    # Obtener empleados reales del departamento
    from employees.models import Employee
    employees = Employee.objects.filter(department=department, is_active=True)
    positions = department.positions.all()
    budgets = []  # Por implementar sistema de presupuestos
    
    # Calcular promedio por empleado
    total_employees = employees.count()
    budget_per_employee = 0
    if total_employees > 0 and department.budget:
        budget_per_employee = department.budget / total_employees
    
    context = {
        'department': department,
        'employees': employees,
        'positions': positions,
        'budgets': budgets,
        'total_employees': total_employees,
        'total_positions': positions.count(),
        'budget_per_employee': budget_per_employee,
    }
    
    return render(request, 'departments/department_detail.html', context)


@login_required
def department_edit(request, pk):
    """Vista para editar un departamento"""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            department = form.save()
            messages.success(request, f'Departamento "{department.name}" actualizado exitosamente.')
            return redirect('departments:detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)
    
    return render(request, 'departments/department_form.html', {
        'form': form,
        'department': department,
        'title': 'Editar Departamento'
    })


@login_required
def department_budget_list(request, department_pk):
    """Vista temporal para presupuestos"""
    department = get_object_or_404(Department, pk=department_pk)
    return render(request, 'base.html', {'department': department})


@login_required
def department_budget_create(request, department_pk):
    """Vista temporal para crear presupuesto"""
    department = get_object_or_404(Department, pk=department_pk)
    return render(request, 'base.html', {'department': department})


@login_required
def department_stats_api(request):
    """API para obtener estadísticas de departamentos"""
    stats = Department.objects.aggregate(
        total_departments=Count('id'),
        active_departments=Count('id', filter=Q(is_active=True)),
        total_budget=Sum('budget')
    )
    
    return JsonResponse({
        'general_stats': stats,
        'type_stats': []
    })
