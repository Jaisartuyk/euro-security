"""
Vistas para el sistema médico con Dr. Claude
EURO SECURITY - Asistente Médico IA
"""
import json
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import transaction
from .decorators import employee_required, permission_required
from .models import Employee
from .medical_models import (
    MedicalDocument, MedicalLeave, DrClaudeConversation,
    MedicalDocumentType, MedicalLeaveStatus
)
from .dr_claude_service import dr_claude


@login_required
@employee_required
def medical_dashboard(request):
    """Dashboard principal del sistema médico"""
    try:
        employee = Employee.objects.get(user=request.user)
        
        # Obtener resumen médico del empleado
        medical_summary = dr_claude.get_employee_medical_summary(employee)
        
        # Documentos recientes
        recent_documents = MedicalDocument.objects.filter(
            employee=employee
        ).order_by('-uploaded_at')[:5]
        
        # Permisos activos
        active_leaves = MedicalLeave.objects.filter(
            employee=employee,
            status__in=[
                MedicalLeaveStatus.ACTIVE,
                MedicalLeaveStatus.AI_APPROVED,
                MedicalLeaveStatus.HR_APPROVED
            ]
        ).order_by('-start_date')
        
        # Estadísticas
        stats = {
            'total_documents': MedicalDocument.objects.filter(employee=employee).count(),
            'pending_documents': MedicalDocument.objects.filter(
                employee=employee, 
                processed_by_ai=False
            ).count(),
            'active_leaves': active_leaves.count(),
            'total_medical_days': sum(leave.total_days for leave in active_leaves)
        }
        
        context = {
            'employee': employee,
            'recent_documents': recent_documents,
            'active_leaves': active_leaves,
            'stats': stats,
            'medical_summary': medical_summary,
            'dr_claude_greeting': dr_claude.personality['greeting'],
            'page_title': 'Dr. Claude - Asistente Médico IA'
        }
        
        return render(request, 'attendance/medical/dashboard.html', context)
        
    except Employee.DoesNotExist:
        messages.error(request, 'Perfil de empleado no encontrado.')
        return redirect('attendance:dashboard')


@csrf_exempt
@login_required
@employee_required
def upload_medical_document(request):
    """Subir documento médico para análisis IA"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        employee = Employee.objects.get(user=request.user)
        
        # Validar archivo
        if 'document' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró archivo para subir'
            })
        
        document_file = request.FILES['document']
        document_type = request.POST.get('document_type', MedicalDocumentType.CERTIFICATE)
        
        # Validar tipo de archivo
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_extension = document_file.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de archivo no permitido. Use PDF, JPG o PNG.'
            })
        
        # Validar tamaño (máximo 10MB)
        if document_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande. Máximo 10MB.'
            })
        
        with transaction.atomic():
            # Crear documento médico
            medical_doc = MedicalDocument.objects.create(
                employee=employee,
                document_type=document_type,
                document_file=document_file
            )
            
            # Procesar con Dr. Claude
            analysis_result = dr_claude.analyze_medical_certificate(medical_doc)
            
            if analysis_result.get('success', True):
                # Crear permiso médico si es necesario
                if document_type == MedicalDocumentType.CERTIFICATE:
                    medical_leave = dr_claude.create_medical_leave(medical_doc)
                    
                    return JsonResponse({
                        'success': True,
                        'message': '¡Documento procesado exitosamente por Dr. Claude!',
                        'document_id': medical_doc.id,
                        'analysis': medical_doc.ai_analysis,
                        'confidence': medical_doc.ai_confidence_score,
                        'leave_created': medical_leave is not None,
                        'leave_id': medical_leave.id if medical_leave else None,
                        'extracted_data': medical_doc.ai_extracted_data
                    })
                else:
                    return JsonResponse({
                        'success': True,
                        'message': 'Documento subido y analizado correctamente',
                        'document_id': medical_doc.id,
                        'analysis': medical_doc.ai_analysis,
                        'confidence': medical_doc.ai_confidence_score
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'error': analysis_result.get('error', 'Error en el análisis del documento')
                })
        
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Perfil de empleado no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error procesando documento: {str(e)}'
        })


@csrf_exempt
@login_required
@employee_required
def chat_with_claude(request):
    """Chat en tiempo real con Dr. Claude"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        employee = Employee.objects.get(user=request.user)
        data = json.loads(request.body)
        
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Mensaje vacío'
            })
        
        # Procesar con Dr. Claude
        response = dr_claude.chat_with_employee(employee, message, session_id)
        
        return JsonResponse(response)
        
    except Employee.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Perfil de empleado no encontrado'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Formato de datos inválido'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error en chat: {str(e)}'
        })


@login_required
@employee_required
def medical_document_detail(request, document_id):
    """Ver detalle de documento médico"""
    try:
        employee = Employee.objects.get(user=request.user)
        document = get_object_or_404(
            MedicalDocument,
            id=document_id,
            employee=employee
        )
        
        # Obtener permiso médico asociado si existe
        medical_leave = None
        if document.leaves.exists():
            medical_leave = document.leaves.first()
        
        context = {
            'document': document,
            'medical_leave': medical_leave,
            'page_title': f'Documento Médico - {document.get_document_type_display()}'
        }
        
        return render(request, 'attendance/medical/document_detail.html', context)
        
    except Employee.DoesNotExist:
        messages.error(request, 'Perfil de empleado no encontrado.')
        return redirect('attendance:medical_dashboard')


@login_required
@employee_required
def medical_leave_detail(request, leave_id):
    """Ver detalle de permiso médico"""
    try:
        employee = Employee.objects.get(user=request.user)
        leave = get_object_or_404(
            MedicalLeave,
            id=leave_id,
            employee=employee
        )
        
        context = {
            'leave': leave,
            'page_title': f'Permiso Médico - {leave.start_date} a {leave.end_date}'
        }
        
        return render(request, 'attendance/medical/leave_detail.html', context)
        
    except Employee.DoesNotExist:
        messages.error(request, 'Perfil de empleado no encontrado.')
        return redirect('attendance:medical_dashboard')


@login_required
@employee_required
def medical_history(request):
    """Historial médico completo del empleado"""
    try:
        employee = Employee.objects.get(user=request.user)
        
        # Documentos médicos
        documents = MedicalDocument.objects.filter(
            employee=employee
        ).order_by('-uploaded_at')
        
        # Permisos médicos
        leaves = MedicalLeave.objects.filter(
            employee=employee
        ).order_by('-start_date')
        
        # Conversaciones con Dr. Claude
        conversations = DrClaudeConversation.objects.filter(
            employee=employee
        ).order_by('-timestamp')[:20]
        
        context = {
            'employee': employee,
            'documents': documents,
            'leaves': leaves,
            'conversations': conversations,
            'page_title': 'Historial Médico Completo'
        }
        
        return render(request, 'attendance/medical/history.html', context)
        
    except Employee.DoesNotExist:
        messages.error(request, 'Perfil de empleado no encontrado.')
        return redirect('attendance:medical_dashboard')


@csrf_exempt
@login_required
@employee_required
def rate_claude_response(request):
    """Calificar respuesta de Dr. Claude"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        rating = data.get('rating')
        
        if not conversation_id or not rating:
            return JsonResponse({
                'success': False,
                'error': 'Datos faltantes'
            })
        
        # Validar rating
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return JsonResponse({
                'success': False,
                'error': 'Calificación debe ser entre 1 y 5'
            })
        
        # Actualizar conversación
        conversation = get_object_or_404(
            DrClaudeConversation,
            id=conversation_id,
            employee__user=request.user
        )
        
        conversation.user_rating = rating
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'message': '¡Gracias por tu calificación!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error guardando calificación: {str(e)}'
        })


# Vistas para RRHH
@login_required
@permission_required('supervisor')
def hr_medical_dashboard(request):
    """Dashboard médico para RRHH"""
    # Documentos pendientes de revisión
    pending_documents = MedicalDocument.objects.filter(
        processed_by_ai=False
    ).order_by('-uploaded_at')
    
    # Permisos que requieren revisión humana
    pending_leaves = MedicalLeave.objects.filter(
        status=MedicalLeaveStatus.HUMAN_REVIEW
    ).order_by('-created_at')
    
    # Estadísticas del día
    today = timezone.now().date()
    stats = {
        'documents_today': MedicalDocument.objects.filter(
            uploaded_at__date=today
        ).count(),
        'leaves_approved_today': MedicalLeave.objects.filter(
            status__in=[MedicalLeaveStatus.AI_APPROVED, MedicalLeaveStatus.HR_APPROVED],
            created_at__date=today
        ).count(),
        'pending_review': pending_leaves.count(),
        'ai_accuracy': 0.92  # Calcular dinámicamente
    }
    
    context = {
        'pending_documents': pending_documents,
        'pending_leaves': pending_leaves,
        'stats': stats,
        'page_title': 'Dashboard Médico - RRHH'
    }
    
    return render(request, 'attendance/medical/hr_dashboard.html', context)


@csrf_exempt
@login_required
@permission_required('supervisor')
def approve_medical_leave(request, leave_id):
    """Aprobar/rechazar permiso médico (RRHH)"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        data = json.loads(request.body)
        action = data.get('action')  # 'approve' o 'reject'
        notes = data.get('notes', '')
        
        leave = get_object_or_404(MedicalLeave, id=leave_id)
        
        if action == 'approve':
            leave.approve_by_hr(request.user, notes)
            message = f'Permiso médico aprobado para {leave.employee.get_full_name()}'
        elif action == 'reject':
            leave.status = MedicalLeaveStatus.HR_REJECTED
            leave.reviewed_by = request.user
            leave.reviewed_at = timezone.now()
            leave.hr_notes = notes
            leave.save()
            message = f'Permiso médico rechazado para {leave.employee.get_full_name()}'
        else:
            return JsonResponse({
                'success': False,
                'error': 'Acción no válida'
            })
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error procesando solicitud: {str(e)}'
        })
