"""
Vistas para el sistema de gestión de ausencias y permisos laborales
EURO SECURITY - Sistema completo de permisos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib import messages
from datetime import datetime, timedelta

from core.permissions import employee_required
from .models import LeaveRequest, LeaveType, LeaveStatus, MedicalLeave
from .permissions import attendance_permission_required
from employees.models import Employee
from departments.models import Department


@login_required
@employee_required
def leave_request_form(request):
    """
    Formulario para solicitar ausencia laboral
    Empleados pueden crear nuevas solicitudes
    """
    
    # Obtener empleado actual
    try:
        employee = request.user.employee
    except:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('employees:dashboard')
    
    if request.method == 'POST':
        try:
            # Crear solicitud
            leave_request = LeaveRequest(
                employee=employee,
                area=employee.department,
                immediate_supervisor=employee.department.head if employee.department else None,
            )
            
            # Datos del formulario
            leave_request.leave_type = request.POST.get('leave_type')
            leave_request.permission_mode = request.POST.get('permission_mode', 'DAYS')
            leave_request.reason_description = request.POST.get('reason_description', '')
            leave_request.project = request.POST.get('project', '')
            
            # Permisos por días
            if leave_request.permission_mode == 'DAYS':
                leave_request.start_date = datetime.strptime(
                    request.POST.get('start_date'), '%Y-%m-%d'
                ).date()
                leave_request.end_date = datetime.strptime(
                    request.POST.get('end_date'), '%Y-%m-%d'
                ).date()
            
            # Permisos por horas
            else:
                leave_request.permission_date = datetime.strptime(
                    request.POST.get('permission_date'), '%Y-%m-%d'
                ).date()
                leave_request.start_time = datetime.strptime(
                    request.POST.get('start_time'), '%H:%M'
                ).time()
                leave_request.end_time = datetime.strptime(
                    request.POST.get('end_time'), '%H:%M'
                ).time()
            
            # Documento de soporte
            if 'supporting_document' in request.FILES:
                leave_request.supporting_document = request.FILES['supporting_document']
            
            # Guardar y enviar
            leave_request.save()
            leave_request.submit()
            
            messages.success(
                request, 
                f"Solicitud {leave_request.request_number} creada exitosamente. "
                f"Estado: {leave_request.get_status_display()}"
            )
            
            return redirect('attendance:my_leave_requests')
            
        except Exception as e:
            messages.error(request, f"Error al crear solicitud: {str(e)}")
    
    # GET - Mostrar formulario
    context = {
        'employee': employee,
        'leave_types': LeaveType.choices,
        'page_title': 'Solicitar Ausencia Laboral',
    }
    
    return render(request, 'attendance/leaves/request_form.html', context)


@login_required
@employee_required
def my_leave_requests(request):
    """
    Mis solicitudes de ausencia
    El empleado ve sus propias solicitudes
    """
    
    try:
        employee = request.user.employee
    except:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('employees:dashboard')
    
    # Obtener solicitudes del empleado
    requests_list = LeaveRequest.objects.filter(
        employee=employee
    ).select_related(
        'area', 'immediate_supervisor',
        'supervisor_reviewed_by', 'hr_reviewed_by'
    ).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests_list = requests_list.filter(status=status_filter)
    
    # Estadísticas
    stats = {
        'total': requests_list.count(),
        'pending': requests_list.filter(
            status__in=[LeaveStatus.DRAFT, LeaveStatus.PENDING_SUPERVISOR, LeaveStatus.PENDING_HR]
        ).count(),
        'approved': requests_list.filter(
            status__in=[LeaveStatus.APPROVED_HR, LeaveStatus.ACTIVE, LeaveStatus.COMPLETED]
        ).count(),
        'rejected': requests_list.filter(
            status__in=[LeaveStatus.REJECTED_SUPERVISOR, LeaveStatus.REJECTED_HR]
        ).count(),
    }
    
    context = {
        'requests': requests_list,
        'stats': stats,
        'leave_statuses': LeaveStatus.choices,
        'current_status': status_filter,
        'page_title': 'Mis Solicitudes de Ausencia',
    }
    
    return render(request, 'attendance/leaves/my_requests.html', context)


@login_required
@attendance_permission_required('supervisor')
def supervisor_leave_dashboard(request):
    """
    Dashboard para supervisores/jefes
    Gestión de solicitudes de su equipo
    """
    
    try:
        supervisor_employee = request.user.employee
    except:
        return HttpResponseForbidden("No tienes perfil de empleado.")
    
    # Solicitudes del equipo del supervisor
    team_requests = LeaveRequest.objects.filter(
        immediate_supervisor=supervisor_employee
    ).select_related(
        'employee', 'area'
    ).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', 'pending')
    if status_filter == 'pending':
        team_requests = team_requests.filter(status=LeaveStatus.PENDING_SUPERVISOR)
    elif status_filter:
        team_requests = team_requests.filter(status=status_filter)
    
    # Estadísticas
    stats = {
        'pending': LeaveRequest.objects.filter(
            immediate_supervisor=supervisor_employee,
            status=LeaveStatus.PENDING_SUPERVISOR
        ).count(),
        'approved_today': LeaveRequest.objects.filter(
            immediate_supervisor=supervisor_employee,
            status=LeaveStatus.APPROVED_SUPERVISOR,
            supervisor_decision_date__date=timezone.now().date()
        ).count(),
        'total_managed': LeaveRequest.objects.filter(
            immediate_supervisor=supervisor_employee,
            status__in=[LeaveStatus.APPROVED_SUPERVISOR, LeaveStatus.REJECTED_SUPERVISOR]
        ).count(),
    }
    
    context = {
        'requests': team_requests,
        'stats': stats,
        'leave_statuses': LeaveStatus.choices,
        'current_status': status_filter,
        'page_title': 'Gestión de Ausencias - Supervisor',
    }
    
    return render(request, 'attendance/leaves/supervisor_dashboard.html', context)


@login_required
@attendance_permission_required('supervisor')
def supervisor_approve_leave(request, leave_id):
    """
    Aprobar solicitud como supervisor
    """
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Verificar que es el supervisor correcto
    try:
        supervisor_employee = request.user.employee
        if leave_request.immediate_supervisor != supervisor_employee:
            return HttpResponseForbidden("No eres el supervisor de este empleado.")
    except:
        return HttpResponseForbidden("No tienes perfil de empleado.")
    
    # Verificar estado
    if leave_request.status != LeaveStatus.PENDING_SUPERVISOR:
        messages.warning(request, "Esta solicitud no está pendiente de tu aprobación.")
        return redirect('attendance:supervisor_leave_dashboard')
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        leave_request.approve_by_supervisor(request.user, comments)
        
        messages.success(
            request,
            f"Solicitud {leave_request.request_number} aprobada. "
            f"Ahora pasa a RRHH para aprobación final."
        )
    
    return redirect('attendance:supervisor_leave_dashboard')


@login_required
@attendance_permission_required('supervisor')
def supervisor_reject_leave(request, leave_id):
    """
    Rechazar solicitud como supervisor
    """
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Verificar que es el supervisor correcto
    try:
        supervisor_employee = request.user.employee
        if leave_request.immediate_supervisor != supervisor_employee:
            return HttpResponseForbidden("No eres el supervisor de este empleado.")
    except:
        return HttpResponseForbidden("No tienes perfil de empleado.")
    
    # Verificar estado
    if leave_request.status != LeaveStatus.PENDING_SUPERVISOR:
        messages.warning(request, "Esta solicitud no está pendiente de tu aprobación.")
        return redirect('attendance:supervisor_leave_dashboard')
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        if not comments:
            messages.error(request, "Debes proporcionar un motivo para rechazar.")
            return redirect('attendance:supervisor_leave_dashboard')
        
        leave_request.reject_by_supervisor(request.user, comments)
        
        messages.success(
            request,
            f"Solicitud {leave_request.request_number} rechazada."
        )
    
    return redirect('attendance:supervisor_leave_dashboard')


@login_required
@attendance_permission_required('manager')
def hr_leave_dashboard(request):
    """
    Dashboard de RRHH para gestión de ausencias
    Vista completa de todas las solicitudes
    """
    
    # Todas las solicitudes
    all_requests = LeaveRequest.objects.select_related(
        'employee', 'area', 'immediate_supervisor',
        'supervisor_reviewed_by', 'hr_reviewed_by'
    ).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status', 'pending_hr')
    leave_type_filter = request.GET.get('leave_type', '')
    
    if status_filter == 'pending_hr':
        all_requests = all_requests.filter(status=LeaveStatus.PENDING_HR)
    elif status_filter == 'pending_supervisor':
        all_requests = all_requests.filter(status=LeaveStatus.PENDING_SUPERVISOR)
    elif status_filter == 'ai_approved':
        all_requests = all_requests.filter(ai_generated=True, ai_confidence__gte=0.85)
    elif status_filter:
        all_requests = all_requests.filter(status=status_filter)
    
    if leave_type_filter:
        all_requests = all_requests.filter(leave_type=leave_type_filter)
    
    # Estadísticas
    stats = {
        'pending_hr': LeaveRequest.objects.filter(status=LeaveStatus.PENDING_HR).count(),
        'pending_supervisor': LeaveRequest.objects.filter(status=LeaveStatus.PENDING_SUPERVISOR).count(),
        'approved_today': LeaveRequest.objects.filter(
            status=LeaveStatus.APPROVED_HR,
            hr_decision_date__date=timezone.now().date()
        ).count(),
        'ai_processed': LeaveRequest.objects.filter(ai_generated=True).count(),
        'medical': LeaveRequest.objects.filter(
            leave_type__in=[
                LeaveType.MEDICAL_DISABILITY,
                LeaveType.MEDICAL_APPOINTMENT,
                LeaveType.MEDICAL_EMERGENCY
            ]
        ).count(),
        'personal': LeaveRequest.objects.filter(
            leave_type__in=[
                LeaveType.DOMESTIC_CALAMITY,
                LeaveType.PERSONAL_MATTER,
                LeaveType.BEREAVEMENT
            ]
        ).count(),
    }
    
    # Por tipo de ausencia
    by_type = LeaveRequest.objects.values('leave_type').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        'requests': all_requests[:50],  # Limitar a 50 para rendimiento
        'stats': stats,
        'by_type': by_type,
        'leave_types': LeaveType.choices,
        'leave_statuses': LeaveStatus.choices,
        'current_status': status_filter,
        'current_type': leave_type_filter,
        'page_title': 'Gestión de Ausencias - RRHH',
    }
    
    return render(request, 'attendance/leaves/hr_dashboard.html', context)


@login_required
@attendance_permission_required('manager')
def hr_approve_leave(request, leave_id):
    """
    Aprobar solicitud como RRHH - Aprobación final
    """
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Verificar estado
    if leave_request.status != LeaveStatus.PENDING_HR:
        messages.warning(request, "Esta solicitud no está pendiente de RRHH.")
        return redirect('attendance:hr_leave_dashboard')
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        leave_request.approve_by_hr(request.user, comments)
        
        messages.success(
            request,
            f"Solicitud {leave_request.request_number} APROBADA DEFINITIVAMENTE. "
            f"El empleado ha sido notificado."
        )
    
    return redirect('attendance:hr_leave_dashboard')


@login_required
@attendance_permission_required('manager')
def hr_reject_leave(request, leave_id):
    """
    Rechazar solicitud como RRHH
    """
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Verificar estado
    if leave_request.status != LeaveStatus.PENDING_HR:
        messages.warning(request, "Esta solicitud no está pendiente de RRHH.")
        return redirect('attendance:hr_leave_dashboard')
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        if not comments:
            messages.error(request, "Debes proporcionar un motivo para rechazar.")
            return redirect('attendance:hr_leave_dashboard')
        
        leave_request.reject_by_hr(request.user, comments)
        
        messages.success(
            request,
            f"Solicitud {leave_request.request_number} rechazada por RRHH."
        )
    
    return redirect('attendance:hr_leave_dashboard')


@login_required
def leave_request_detail(request, leave_id):
    """
    Detalle de una solicitud de ausencia
    Ver toda la información y el historial
    """
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Verificar permisos
    try:
        employee = request.user.employee
        is_owner = leave_request.employee == employee
        is_supervisor = leave_request.immediate_supervisor == employee
        is_hr = request.user.groups.filter(name__in=['Manager', 'Director']).exists()
        
        if not (is_owner or is_supervisor or is_hr or request.user.is_superuser):
            return HttpResponseForbidden("No tienes permiso para ver esta solicitud.")
    except:
        if not request.user.is_superuser:
            return HttpResponseForbidden("No tienes permiso para ver esta solicitud.")
    
    context = {
        'leave': leave_request,
        'can_approve': is_supervisor or is_hr,
        'can_edit': is_owner and leave_request.status == LeaveStatus.DRAFT,
        'page_title': f'Solicitud {leave_request.request_number}',
    }
    
    return render(request, 'attendance/leaves/detail.html', context)
