"""
URLs para el sistema de asistencia
"""
from django.urls import path
from . import views
from . import reports_views
from . import gps_views

app_name = 'attendance'

urlpatterns = [
    # Vista principal de marcación
    path('', views.attendance_clock, name='clock'),
    path('marcar/', views.attendance_clock, name='clock'),
    
    # API para registrar asistencia
    path('api/record/', views.record_attendance, name='record'),
    
    # Dashboard para supervisores
    path('dashboard/', views.attendance_dashboard, name='dashboard'),
    
    # Reportes
    path('reportes/', reports_views.attendance_reports, name='reports'),
    path('reportes/departamento/<int:department_id>/', reports_views.department_attendance_report, name='department_report'),
    path('reportes/exportar/', reports_views.export_attendance_report, name='export_report'),
    
    # Mapas y ubicaciones
    path('mapa/', reports_views.attendance_locations_map, name='locations_map'),
    path('api/ubicaciones/', reports_views.attendance_locations_api, name='locations_api'),
    
    # Rastreo GPS en tiempo real
    path('rastreo-tiempo-real/', gps_views.real_time_tracking_dashboard, name='real_time_tracking'),
    path('api/rastreo-gps/', gps_views.gps_tracking_api, name='gps_tracking_api'),
    path('api/areas-trabajo/', gps_views.work_areas_api, name='work_areas_api'),
    path('api/actualizar-gps/', gps_views.update_gps_location, name='update_gps_location'),
    path('empleado/<int:employee_id>/historial-gps/', gps_views.employee_tracking_history, name='employee_tracking_history'),
    path('alertas-ubicacion/', gps_views.location_alerts_view, name='location_alerts'),
    
    # Gestión de Áreas de Trabajo
    path('areas-trabajo/', gps_views.work_areas_list, name='work_areas_list'),
    path('areas-trabajo/crear/', gps_views.work_area_create, name='work_area_create'),
    path('areas-trabajo/<int:pk>/', gps_views.work_area_detail, name='work_area_detail'),
    path('areas-trabajo/<int:pk>/editar/', gps_views.work_area_edit, name='work_area_edit'),
    path('areas-trabajo/<int:pk>/asignar-empleados/', gps_views.work_area_assign_employees, name='work_area_assign_employees'),
    
    # Vista personal del empleado
    path('mi-asistencia/', views.my_attendance, name='my_attendance'),
    
    # Registro de perfil facial
    path('registro-facial/', views.facial_enrollment, name='facial_enrollment'),
    
    # API para crear perfil automáticamente
    path('api/create-profile/', views.create_profile_from_photos, name='create_profile'),
    
    # Modo de emergencia
    path('api/emergency-record/', views.emergency_record_attendance, name='emergency_record'),
]
