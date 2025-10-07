"""
Vistas para el Centro de Operaciones Inteligente
Sistema de monitoreo en tiempo real con IA
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import timedelta
import json

from employees.models import Employee
from .models_security_photos import SecurityPhoto, SecurityAlert, VideoSession
from .models_gps import GPSTracking, WorkArea
from .ai_services import roboflow_service, facepp_service, firebase_service, agora_service


@login_required
def operations_dashboard(request):
    """Dashboard principal del Centro de Operaciones"""
    
    # Verificar permisos
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('attendance:dashboard')
    
    # Estadísticas generales
    today = timezone.now().date()
    last_24h = timezone.now() - timedelta(hours=24)
    
    stats = {
        'total_photos_today': SecurityPhoto.objects.filter(timestamp__date=today).count(),
        'active_alerts': SecurityAlert.objects.filter(status='PENDING').count(),
        'critical_alerts': SecurityAlert.objects.filter(
            status='PENDING', 
            severity='CRITICAL'
        ).count(),
        'active_employees': GPSTracking.objects.filter(
            timestamp__gte=last_24h
        ).values('employee').distinct().count(),
        'active_video_sessions': VideoSession.objects.filter(status='ACTIVE').count(),
    }
    
    # Alertas recientes
    recent_alerts = SecurityAlert.objects.select_related(
        'employee', 'photo', 'acknowledged_by'
    ).order_by('-created_at')[:10]
    
    # Fotos recientes (todas, no solo con alertas)
    recent_photos = SecurityPhoto.objects.select_related(
        'employee', 'work_area'
    ).order_by('-timestamp')[:20]
    
    # Empleados activos con última ubicación
    active_employees = []
    
    # Obtener última ubicación por empleado (compatible con PostgreSQL)
    from django.db.models import Max
    latest_timestamps = GPSTracking.objects.filter(
        timestamp__gte=last_24h
    ).values('employee').annotate(
        latest_time=Max('timestamp')
    )
    
    latest_gps = []
    for item in latest_timestamps:
        gps = GPSTracking.objects.filter(
            employee_id=item['employee'],
            timestamp=item['latest_time']
        ).select_related('employee', 'work_area').first()
        if gps:
            latest_gps.append(gps)
    
    for gps in latest_gps:
        active_employees.append({
            'employee': gps.employee,
            'latitude': float(gps.latitude),
            'longitude': float(gps.longitude),
            'timestamp': gps.timestamp,
            'work_area': gps.work_area,
            'is_within_area': gps.is_within_work_area
        })
    
    context = {
        'stats': stats,
        'recent_alerts': recent_alerts,
        'recent_photos': recent_photos,
        'active_employees': active_employees,
        'work_areas': WorkArea.objects.filter(is_active=True),
    }
    
    return render(request, 'attendance/operations/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def capture_security_photo(request):
    """API para capturar foto de seguridad desde PWA"""
    
    try:
        # Obtener datos del request
        photo_file = request.FILES.get('photo')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        capture_type = request.POST.get('capture_type', 'MANUAL')
        
        if not photo_file:
            return JsonResponse({'error': 'No se recibió la foto'}, status=400)
        
        # Obtener empleado
        employee = request.user.employee if hasattr(request.user, 'employee') else None
        if not employee:
            return JsonResponse({'error': 'Usuario no es empleado'}, status=403)
        
        # Crear foto de seguridad
        security_photo = SecurityPhoto.objects.create(
            employee=employee,
            photo=photo_file,
            latitude=latitude,
            longitude=longitude,
            capture_type=capture_type,
            device_info=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        # Crear registro GPS si hay ubicación
        if latitude and longitude:
            try:
                GPSTracking.objects.create(
                    employee=employee,
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=timezone.now(),
                    accuracy=10.0  # Valor por defecto
                )
            except Exception as gps_error:
                # No fallar si no se puede crear GPS
                print(f"Error creando GPS tracking: {gps_error}")
        
        # Analizar con IA en segundo plano (opcional)
        if request.POST.get('analyze_ai') == 'true':
            security_photo.analyze_with_ai()
        
        return JsonResponse({
            'success': True,
            'photo_id': security_photo.id,
            'message': 'Foto capturada exitosamente',
            'has_alerts': security_photo.has_alerts,
            'alert_level': security_photo.alert_level,
            'ai_analyzed': security_photo.ai_analyzed
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def analyze_photo_ai(request, photo_id):
    """Analizar foto con IA"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        photo = get_object_or_404(SecurityPhoto, id=photo_id)
        
        # Analizar con IA
        results = photo.analyze_with_ai()
        
        if results:
            return JsonResponse({
                'success': True,
                'results': results,
                'has_alerts': photo.has_alerts,
                'alert_level': photo.alert_level
            })
        else:
            return JsonResponse({'error': 'Error en análisis IA'}, status=500)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_live_locations(request):
    """API para obtener ubicaciones en tiempo real"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        # Últimas ubicaciones (últimos 5 minutos)
        last_5min = timezone.now() - timedelta(minutes=5)
        
        # Obtener última ubicación por empleado (compatible con PostgreSQL)
        from django.db.models import Max
        latest_timestamps = GPSTracking.objects.filter(
            timestamp__gte=last_5min
        ).values('employee').annotate(
            latest_time=Max('timestamp')
        )
        
        locations = []
        for item in latest_timestamps:
            gps = GPSTracking.objects.filter(
                employee_id=item['employee'],
                timestamp=item['latest_time']
            ).select_related('employee', 'work_area').first()
            
            if not gps:
                continue
            
            # Obtener última foto si existe
            last_photo = SecurityPhoto.objects.filter(
                employee=gps.employee,
                timestamp__gte=last_5min
            ).order_by('-timestamp').first()
            
            locations.append({
                'employee_id': gps.employee.id,
                'employee_name': gps.employee.get_full_name(),
                'employee_code': gps.employee.employee_id,
                'latitude': float(gps.latitude),
                'longitude': float(gps.longitude),
                'accuracy': float(gps.accuracy) if gps.accuracy else None,
                'timestamp': gps.timestamp.isoformat(),
                'work_area': gps.work_area.name if gps.work_area else None,
                'is_within_area': gps.is_within_work_area,
                'battery_level': gps.battery_level,
                'has_photo': last_photo is not None,
                'photo_url': last_photo.thumbnail.url if last_photo and last_photo.thumbnail else None,
                'has_alerts': last_photo.has_alerts if last_photo else False,
                'alert_level': last_photo.alert_level if last_photo else 'NONE'
            })
        
        return JsonResponse({
            'success': True,
            'locations': locations,
            'count': len(locations),
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_active_alerts(request):
    """API para obtener alertas activas"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        alerts = SecurityAlert.objects.filter(
            status__in=['PENDING', 'ACKNOWLEDGED', 'IN_PROGRESS']
        ).select_related('employee', 'photo', 'acknowledged_by').order_by('-created_at')[:50]
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': alert.id,
                'employee_id': alert.employee.id,
                'employee_name': alert.employee.get_full_name(),
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'status': alert.status,
                'created_at': alert.created_at.isoformat(),
                'photo_url': alert.photo.thumbnail.url if alert.photo and alert.photo.thumbnail else None,
                'acknowledged_by': alert.acknowledged_by.get_full_name() if alert.acknowledged_by else None,
            })
        
        return JsonResponse({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def acknowledge_alert(request, alert_id):
    """Reconocer una alerta"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        alert = get_object_or_404(SecurityAlert, id=alert_id)
        alert.acknowledge(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Alerta reconocida',
            'status': alert.status
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def resolve_alert(request, alert_id):
    """Resolver una alerta"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        alert = get_object_or_404(SecurityAlert, id=alert_id)
        notes = request.POST.get('notes', '')
        
        alert.resolve(notes)
        
        return JsonResponse({
            'success': True,
            'message': 'Alerta resuelta',
            'status': alert.status
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def request_video_session(request, employee_id):
    """Solicitar sesión de video a un empleado"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    try:
        employee = get_object_or_404(Employee, id=employee_id)
        requester = request.user.employee if hasattr(request.user, 'employee') else None
        
        if not requester:
            return JsonResponse({'error': 'Usuario no es empleado'}, status=403)
        
        # Crear sesión de video con Agora
        try:
            session_data = agora_service.create_video_session(employee.id, requester.id)
        except ValueError as ve:
            # Error de configuración de Agora
            return JsonResponse({
                'error': str(ve),
                'details': 'Verifica que AGORA_APP_ID y AGORA_APP_CERTIFICATE estén configurados en Railway'
            }, status=500)
        
        # Crear registro en BD
        video_session = VideoSession.objects.create(
            employee=employee,
            requester=requester,
            channel_name=session_data['channel_name'],
            employee_token=session_data['employee_token'],
            requester_token=session_data['requester_token'],
            status='REQUESTED'
        )
        
        # Enviar notificación push al empleado (si tiene token)
        # TODO: Implementar envío de notificación
        
        return JsonResponse({
            'success': True,
            'session_id': video_session.id,
            'channel_name': video_session.channel_name,
            'app_id': session_data['app_id'],
            'requester_token': video_session.requester_token,
            'requester_uid': session_data['requester_uid'],
            'employee_uid': session_data['employee_uid'],
            'message': 'Solicitud de video enviada'
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error en request_video_session: {error_details}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_video_session(request, session_id):
    """Obtener datos de sesión de video"""
    
    try:
        session = get_object_or_404(VideoSession, id=session_id)
        
        # Verificar permisos
        if not (request.user.is_staff or request.user.is_superuser or 
                (hasattr(request.user, 'employee') and request.user.employee == session.employee)):
            return JsonResponse({'error': 'Sin permisos'}, status=403)
        
        # Determinar token según usuario
        is_requester = hasattr(request.user, 'employee') and request.user.employee == session.requester
        token = session.requester_token if is_requester else session.employee_token
        
        return JsonResponse({
            'success': True,
            'session': {
                'id': session.id,
                'channel_name': session.channel_name,
                'token': token,
                'app_id': agora_service.app_id,
                'status': session.status,
                'employee_name': session.employee.get_full_name(),
                'requester_name': session.requester.get_full_name(),
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def end_video_session(request, session_id):
    """Finalizar sesión de video"""
    
    try:
        session = get_object_or_404(VideoSession, id=session_id)
        
        # Verificar permisos
        if not (request.user.is_staff or request.user.is_superuser or 
                (hasattr(request.user, 'employee') and 
                 request.user.employee in [session.employee, session.requester])):
            return JsonResponse({'error': 'Sin permisos'}, status=403)
        
        session.end()
        
        return JsonResponse({
            'success': True,
            'message': 'Sesión finalizada',
            'duration_seconds': session.duration_seconds
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def security_photos_list(request):
    """Lista de fotos de seguridad"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('attendance:dashboard')
    
    # Filtros
    employee_id = request.GET.get('employee')
    has_alerts = request.GET.get('has_alerts')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    photos = SecurityPhoto.objects.select_related('employee', 'work_area').order_by('-timestamp')
    
    if employee_id:
        photos = photos.filter(employee_id=employee_id)
    if has_alerts:
        photos = photos.filter(has_alerts=True)
    if date_from:
        photos = photos.filter(timestamp__date__gte=date_from)
    if date_to:
        photos = photos.filter(timestamp__date__lte=date_to)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(photos, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'employees': Employee.objects.filter(is_active=True).order_by('first_name'),
    }
    
    return render(request, 'attendance/operations/photos_list.html', context)


@login_required
def operations_analytics(request):
    """Panel de estadísticas y analytics del Centro de Operaciones"""
    
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('attendance:dashboard')
    
    # Rango de tiempo
    time_range = request.GET.get('range', 'week')
    
    if time_range == 'today':
        start_date = timezone.now().replace(hour=0, minute=0, second=0)
    elif time_range == 'week':
        start_date = timezone.now() - timedelta(days=7)
    elif time_range == 'month':
        start_date = timezone.now() - timedelta(days=30)
    else:
        start_date = timezone.now() - timedelta(days=7)
    
    # Estadísticas básicas
    total_photos = SecurityPhoto.objects.filter(timestamp__gte=start_date).count()
    total_alerts = SecurityAlert.objects.filter(created_at__gte=start_date).count()
    
    # Precisión IA (fotos analizadas vs total)
    analyzed_photos = SecurityPhoto.objects.filter(
        timestamp__gte=start_date,
        ai_analyzed=True
    ).count()
    ai_accuracy = int((analyzed_photos / total_photos * 100)) if total_photos > 0 else 0
    
    # Tiempo promedio de respuesta (alertas reconocidas)
    from django.db.models import Avg, F, ExpressionWrapper, DurationField
    avg_response = SecurityAlert.objects.filter(
        created_at__gte=start_date,
        acknowledged_at__isnull=False
    ).annotate(
        response_time=ExpressionWrapper(
            F('acknowledged_at') - F('created_at'),
            output_field=DurationField()
        )
    ).aggregate(avg=Avg('response_time'))
    
    avg_response_seconds = int(avg_response['avg'].total_seconds()) if avg_response['avg'] else 0
    
    context = {
        'time_range': time_range,
        'stats': {
            'total_photos': total_photos,
            'total_alerts': total_alerts,
            'ai_accuracy': ai_accuracy,
            'avg_response_seconds': avg_response_seconds,
        }
    }


@login_required
def check_pending_video_request(request):
    """Verificar si hay solicitudes de video pendientes para el empleado"""
    
    try:
        employee = request.user.employee if hasattr(request.user, 'employee') else None
        
        if not employee:
            return JsonResponse({'has_pending': False})
        
        # Buscar sesión pendiente para este empleado
        pending_session = VideoSession.objects.filter(
            employee=employee,
            status='REQUESTED'
        ).order_by('-created_at').first()
        
        if pending_session:
            # Obtener datos de la sesión
            session_data = agora_service.create_video_session(
                pending_session.employee.id,
                pending_session.requester.id
            )
            
            return JsonResponse({
                'has_pending': True,
                'session': {
                    'id': pending_session.id,
                    'channel_name': pending_session.channel_name,
                    'app_id': session_data['app_id'],
                    'employee_token': pending_session.employee_token,
                    'employee_uid': session_data['employee_uid'],
                    'requester_name': pending_session.requester.get_full_name()
                }
            })
        
        return JsonResponse({'has_pending': False})
        
    except Exception as e:
        return JsonResponse({'error': str(e), 'has_pending': False}, status=500)
    
    return render(request, 'attendance/operations/analytics.html', context)
