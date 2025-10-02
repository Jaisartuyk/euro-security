from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from employees.models import Employee
from .models import FormCategory, FormDocument, FormDownloadLog
import os


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def has_form_access(user, required_permission):
    """Verificar si el usuario tiene acceso a formularios"""
    if not user.is_authenticated:
        return False
    
    # Superusers siempre tienen acceso
    if user.is_superuser:
        return True
    
    try:
        employee = Employee.objects.get(user=user)
        permission_level = employee.get_permission_level()
        
        # Mapeo de permisos
        access_map = {
            'admin': ['full'],
            'hr': ['full', 'management'],
            'management': ['full', 'management'],
            'supervisor': ['full', 'management', 'supervisor'],
            'all': ['full', 'management', 'supervisor', 'advanced', 'standard', 'basic']
        }
        
        return permission_level in access_map.get(required_permission, [])
    except Employee.DoesNotExist:
        return False


@login_required
def forms_dashboard(request):
    """Dashboard principal de formularios (estáticos y dinámicos)"""
    # Verificar permisos básicos (HR o admin)
    if not has_form_access(request.user, 'hr'):
        messages.error(request, 'No tienes permisos para acceder a los formularios.')
        return redirect('attendance:dashboard')
    
    # Obtener categorías activas
    categories = FormCategory.objects.filter(is_active=True)
    
    # Obtener formularios estáticos recientes
    recent_forms = FormDocument.objects.filter(
        is_active=True
    ).select_related('category', 'created_by')[:5]
    
    # Obtener plantillas dinámicas activas
    dynamic_templates = FormTemplate.objects.filter(
        is_active=True
    ).select_related('category', 'created_by')[:5]
    
    # Obtener asignaciones pendientes para el usuario
    pending_assignments = FormAssignment.objects.filter(
        assigned_to=request.user,
        is_completed=False
    ).select_related('template', 'assigned_by')[:5]
    
    # Obtener envíos recientes del usuario
    recent_submissions = FormSubmission.objects.filter(
        submitted_by=request.user
    ).select_related('template').order_by('-created_at')[:5]
    
    # Estadísticas combinadas
    stats = {
        'total_static_forms': FormDocument.objects.filter(is_active=True).count(),
        'total_dynamic_templates': FormTemplate.objects.filter(is_active=True).count(),
        'total_categories': categories.count(),
        'total_downloads': FormDownloadLog.objects.count(),
        'pending_assignments': pending_assignments.count(),
        'total_submissions': FormSubmission.objects.count(),
        'recent_downloads': FormDownloadLog.objects.select_related(
            'form', 'user'
        ).order_by('-downloaded_at')[:5]
    }
    
    # Estadísticas adicionales para RRHH
    if has_form_access(request.user, 'hr'):
        stats.update({
            'pending_reviews': FormSubmission.objects.filter(status='submitted').count(),
            'completed_today': FormSubmission.objects.filter(
                status='completed',
                updated_at__date=timezone.now().date()
            ).count()
        })
    
    context = {
        'categories': categories,
        'recent_forms': recent_forms,
        'dynamic_templates': dynamic_templates,
        'pending_assignments': pending_assignments,
        'recent_submissions': recent_submissions,
        'stats': stats,
        'is_hr': has_form_access(request.user, 'hr'),
        'user_permission': Employee.objects.get(user=request.user).get_permission_level() if hasattr(request.user, 'employee') else 'basic'
    }
    
    return render(request, 'forms/dashboard.html', context)


@login_required
def forms_by_category(request, category_id):
    """Formularios por categoría"""
    if not has_form_access(request.user, 'hr'):
        messages.error(request, 'No tienes permisos para acceder a los formularios.')
        return redirect('attendance:dashboard')
    
    category = get_object_or_404(FormCategory, id=category_id, is_active=True)
    
    # Filtrar formularios según permisos del usuario
    forms_query = FormDocument.objects.filter(
        category=category,
        is_active=True
    ).select_related('category', 'created_by')
    
    # Filtrar por permisos
    user_permission = 'basic'
    try:
        employee = Employee.objects.get(user=request.user)
        user_permission = employee.get_permission_level()
    except Employee.DoesNotExist:
        pass
    
    # Solo mostrar formularios que el usuario puede ver
    accessible_forms = []
    for form in forms_query:
        if has_form_access(request.user, form.required_permission):
            accessible_forms.append(form)
    
    # Paginación
    paginator = Paginator(accessible_forms, 12)
    page_number = request.GET.get('page')
    forms = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'forms': forms,
        'user_permission': user_permission
    }
    
    return render(request, 'forms/category_forms.html', context)


@login_required
def preview_form(request, form_id):
    """Vista previa del formulario en el navegador"""
    form = get_object_or_404(FormDocument, id=form_id, is_active=True)
    
    # Verificar permisos
    if not has_form_access(request.user, form.required_permission):
        messages.error(request, 'No tienes permisos para ver este formulario.')
        return redirect('forms:dashboard')
    
    # Verificar que el archivo existe
    if not form.file or not os.path.exists(form.file.path):
        messages.error(request, 'El archivo no existe o no está disponible.')
        return redirect('forms:dashboard')
    
    try:
        # Preparar respuesta para vista previa
        with open(form.file.path, 'rb') as file:
            response = HttpResponse(
                file.read(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'inline; filename="{os.path.basename(form.file.name)}"'
            return response
            
    except Exception as e:
        messages.error(request, f'Error al mostrar el archivo: {str(e)}')
        return redirect('forms:dashboard')


@login_required
def download_form(request, form_id):
    """Descargar formulario"""
    form = get_object_or_404(FormDocument, id=form_id, is_active=True)
    
    # Verificar permisos
    if not has_form_access(request.user, form.required_permission):
        messages.error(request, 'No tienes permisos para descargar este formulario.')
        return redirect('forms:dashboard')
    
    # Verificar que el archivo existe
    if not form.file or not os.path.exists(form.file.path):
        messages.error(request, 'El archivo no existe o no está disponible.')
        return redirect('forms:dashboard')
    
    try:
        # Registrar descarga
        FormDownloadLog.objects.create(
            form=form,
            user=request.user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        # Incrementar contador
        form.increment_download_count()
        
        # Preparar respuesta de descarga
        with open(form.file.path, 'rb') as file:
            response = HttpResponse(
                file.read(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(form.file.name)}"'
            return response
            
    except Exception as e:
        messages.error(request, f'Error al descargar el archivo: {str(e)}')
        return redirect('forms:dashboard')


@login_required
def search_forms(request):
    """Búsqueda de formularios"""
    if not has_form_access(request.user, 'hr'):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'forms': []})
    
    # Búsqueda en título y descripción
    forms = FormDocument.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).select_related('category')[:10]
    
    # Filtrar por permisos
    results = []
    for form in forms:
        if has_form_access(request.user, form.required_permission):
            results.append({
                'id': form.id,
                'title': form.title,
                'description': form.description[:100] + '...' if len(form.description) > 100 else form.description,
                'category': form.category.name,
                'version': form.version,
                'download_count': form.download_count
            })
    
    return JsonResponse({'forms': results})


@login_required
def forms_stats(request):
    """Estadísticas de formularios (solo admin)"""
    if not has_form_access(request.user, 'admin'):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    # Estadísticas por categoría
    category_stats = FormCategory.objects.filter(
        is_active=True
    ).annotate(
        form_count=Count('formdocument')
    ).values('name', 'form_count')
    
    # Formularios más descargados
    top_downloads = FormDocument.objects.filter(
        is_active=True
    ).order_by('-download_count')[:5].values(
        'title', 'download_count'
    )
    
    # Descargas recientes
    recent_activity = FormDownloadLog.objects.select_related(
        'form', 'user'
    ).order_by('-downloaded_at')[:10]
    
    recent_data = []
    for log in recent_activity:
        recent_data.append({
            'form_title': log.form.title,
            'user': log.user.get_full_name() or log.user.username,
            'downloaded_at': log.downloaded_at.strftime('%d/%m/%Y %H:%M')
        })
    
    return JsonResponse({
        'category_stats': list(category_stats),
        'top_downloads': list(top_downloads),
        'recent_activity': recent_data
    })


# ============================================================================
# VISTAS PARA FORMULARIOS DINÁMICOS
# ============================================================================

@login_required
def dynamic_forms_dashboard(request):
    """Dashboard para formularios dinámicos"""
    if not has_form_access(request.user, 'hr'):
        messages.error(request, 'No tienes permisos para acceder a los formularios dinámicos.')
        return redirect('attendance:dashboard')
    
    return render(request, 'forms/dashboard.html', {'dynamic_mode': True})


@login_required
def template_detail(request, template_id):
    """Ver detalles de una plantilla de formulario"""
    template = get_object_or_404(FormTemplate, id=template_id, is_active=True)
    return render(request, 'forms/template_detail.html', {'template': template})


@login_required
def fill_form(request, template_id, assignment_id=None):
    """Completar un formulario dinámico"""
    template = get_object_or_404(FormTemplate, id=template_id, is_active=True)
    return render(request, 'forms/fill_form.html', {'template': template})


@login_required
def submission_detail(request, submission_id):
    """Ver detalles de un envío de formulario"""
    submission = get_object_or_404(FormSubmission, id=submission_id)
    return render(request, 'forms/submission_detail.html', {'submission': submission})


@login_required
@require_http_methods(["POST"])
def review_submission(request, submission_id):
    """Revisar y aprobar/rechazar un envío"""
    if not has_form_access(request.user, 'hr'):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    submission = get_object_or_404(FormSubmission, id=submission_id)
    return redirect('forms:submission_detail', submission_id=submission_id)


@login_required
def assign_form(request, template_id):
    """Asignar formulario a empleados"""
    if not has_form_access(request.user, 'hr'):
        messages.error(request, 'No tienes permisos para asignar formularios.')
        return redirect('forms:dashboard')
    
    template = get_object_or_404(FormTemplate, id=template_id, is_active=True)
    return render(request, 'forms/assign_form.html', {'template': template})
