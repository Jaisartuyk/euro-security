from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Employee
from .forms import EmployeeForm, EmployeeFilterForm
from departments.models import Department
from positions.models import Position


@login_required
def employee_list(request):
    """Vista para listar todos los empleados"""
    employees = Employee.objects.select_related('department', 'position', 'user').all()
    
    # Filtros
    search = request.GET.get('search')
    department_id = request.GET.get('department')
    position_id = request.GET.get('position')
    status = request.GET.get('status')
    
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) |
            Q(employee_id__icontains=search) |
            Q(email__icontains=search) |
            Q(national_id__icontains=search)
        )
    
    if department_id:
        employees = employees.filter(department_id=department_id)
    
    if position_id:
        employees = employees.filter(position_id=position_id)
    
    if status:
        is_active = status == 'active'
        employees = employees.filter(is_active=is_active)
    
    # Ordenamiento
    employees = employees.order_by('last_name', 'first_name')
    
    # Paginación
    paginator = Paginator(employees, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Datos para filtros
    departments = Department.objects.filter(is_active=True).order_by('name')
    positions = Position.objects.filter(is_active=True).order_by('title')
    
    context = {
        'page_obj': page_obj,
        'departments': departments,
        'positions': positions,
        'search': search,
        'selected_department': department_id,
        'selected_position': position_id,
        'selected_status': status,
    }
    
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_create(request):
    """Vista para crear un nuevo empleado"""
    user_credentials = None
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            
            # Generar cuenta de usuario automáticamente
            user_credentials = employee.create_user_account()
            
            if user_credentials:
                messages.success(
                    request, 
                    f'Empleado "{employee.get_full_name()}" creado exitosamente. '
                    f'Usuario: {user_credentials["username"]} | '
                    f'Contraseña: {user_credentials["password"]}'
                )
                # Guardar credenciales en la sesión para mostrarlas en el detalle
                request.session['new_user_credentials'] = {
                    'username': user_credentials['username'],
                    'password': user_credentials['password'],
                    'employee_id': employee.pk
                }
            else:
                messages.success(request, f'Empleado "{employee.get_full_name()}" creado exitosamente.')
            
            return redirect('employees:detail', pk=employee.pk)
    else:
        form = EmployeeForm()
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'title': 'Crear Empleado',
        'user_credentials': user_credentials
    })


@login_required
def employee_detail(request, pk):
    """Vista para ver detalles de un empleado"""
    employee = get_object_or_404(Employee.objects.select_related('department', 'position', 'user'), pk=pk)
    
    # Verificar si hay credenciales nuevas en la sesión
    new_credentials = None
    reset_credentials = None
    
    if 'new_user_credentials' in request.session:
        credentials = request.session['new_user_credentials']
        if credentials.get('employee_id') == pk:
            new_credentials = credentials
            # Limpiar las credenciales de la sesión después de mostrarlas
            del request.session['new_user_credentials']
    
    if 'reset_credentials' in request.session:
        credentials = request.session['reset_credentials']
        if credentials.get('employee_id') == pk:
            reset_credentials = credentials
            # Limpiar las credenciales de la sesión después de mostrarlas
            del request.session['reset_credentials']
    
    context = {
        'employee': employee,
        'new_credentials': new_credentials,
        'reset_credentials': reset_credentials,
    }
    
    return render(request, 'employees/employee_detail.html', context)


@login_required
def employee_edit(request, pk):
    """Vista para editar un empleado"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Empleado "{employee.get_full_name()}" actualizado exitosamente.')
            return redirect('employees:detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'employees/employee_form.html', {
        'form': form,
        'employee': employee,
        'title': 'Editar Empleado'
    })


@login_required
def create_user_for_employee(request, pk):
    """Vista para crear usuario manualmente para un empleado"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if employee.user:
        messages.warning(request, f'El empleado "{employee.get_full_name()}" ya tiene una cuenta de usuario: {employee.user.username}')
        return redirect('employees:detail', pk=employee.pk)
    
    if request.method == 'POST':
        # Crear cuenta de usuario
        user_credentials = employee.create_user_account()
        
        if user_credentials:
            messages.success(
                request, 
                f'Usuario creado exitosamente para "{employee.get_full_name()}". '
                f'Usuario: {user_credentials["username"]} | '
                f'Contraseña: {user_credentials["password"]}'
            )
            # Guardar credenciales en la sesión para mostrarlas en el detalle
            request.session['new_user_credentials'] = {
                'username': user_credentials['username'],
                'password': user_credentials['password'],
                'employee_id': employee.pk
            }
        else:
            messages.error(request, f'No se pudo crear usuario para "{employee.get_full_name()}".')
        
        return redirect('employees:detail', pk=employee.pk)
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'employees/create_user_confirm.html', context)


@login_required
def reset_user_password(request, pk):
    """Vista para resetear la contraseña de un usuario"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if not employee.user:
        messages.error(request, f'El empleado "{employee.get_full_name()}" no tiene una cuenta de usuario.')
        return redirect('employees:detail', pk=employee.pk)
    
    if request.method == 'POST':
        # Resetear contraseña
        new_credentials = employee.reset_user_password()
        
        if new_credentials:
            messages.success(
                request, 
                f'Contraseña reseteada exitosamente para "{employee.get_full_name()}". '
                f'Usuario: {new_credentials["username"]} | '
                f'Nueva Contraseña: {new_credentials["password"]}'
            )
            # Guardar credenciales en la sesión para mostrarlas en el detalle
            request.session['reset_credentials'] = {
                'username': new_credentials['username'],
                'password': new_credentials['password'],
                'employee_id': employee.pk,
                'action': 'reset'
            }
        else:
            messages.error(request, f'No se pudo resetear la contraseña para "{employee.get_full_name()}".')
        
        return redirect('employees:detail', pk=employee.pk)
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'employees/reset_password_confirm.html', context)


@login_required
def employee_stats_api(request):
    """API para obtener estadísticas de empleados"""
    from django.db.models import Count, Sum, Avg
    
    stats = Employee.objects.aggregate(
        total_employees=Count('id'),
        active_employees=Count('id', filter=Q(is_active=True)),
        avg_salary=Avg('current_salary', filter=Q(is_active=True))
    )
    
    # Estadísticas por departamento
    dept_stats = Employee.objects.filter(is_active=True).values(
        'department__name'
    ).annotate(
        count=Count('id'),
        avg_salary=Avg('current_salary')
    ).order_by('-count')[:5]
    
    # Estadísticas por género
    gender_stats = Employee.objects.filter(is_active=True).values(
        'gender'
    ).annotate(
        count=Count('id')
    )
    
    return JsonResponse({
        'general_stats': stats,
        'department_stats': list(dept_stats),
        'gender_stats': list(gender_stats)
    })
