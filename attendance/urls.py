"""
URLs para el sistema de asistencia
"""
from django.urls import path
from . import views
from . import reports_views
from . import gps_views
from . import shift_views
from . import medical_views

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
    
    # GPS en segundo plano
    path('actualizar-gps/', gps_views.update_gps_location, name='update_gps_location'),
    
    # Sistema de Turnos
    path('turnos/', shift_views.shift_management_dashboard, name='shift_management_dashboard'),
    path('turnos/plantillas/', shift_views.shift_templates_list, name='shift_templates_list'),
    path('turnos/plantillas/<int:template_id>/', shift_views.shift_template_detail, name='shift_template_detail'),
    path('turnos/crear-horario/', shift_views.create_work_schedule, name='create_work_schedule'),
    path('turnos/crear-horario/<int:template_id>/', shift_views.create_work_schedule, name='create_work_schedule_with_template'),
    path('turnos/horarios/', shift_views.work_schedules_list, name='work_schedules_list'),
    path('turnos/asignar-empleado/', shift_views.assign_employee_to_shift, name='assign_employee_to_shift'),
    
    # Centro de asignación de empleados
    path('turnos/asignar/', shift_views.work_schedules_list, {'show_assignment': True}, name='employee_assignment_center'),
    
    # APIs para asignación de empleados
    path('api/empleados-disponibles/', shift_views.get_available_employees, name='get_available_employees'),
    path('api/asignacion-masiva/', shift_views.bulk_assign_employees, name='bulk_assign_employees'),
    
    # Sistema Médico con Dr. Claude IA
    path('medico/', medical_views.medical_dashboard, name='medical_dashboard'),
    path('medico/subir-documento/', medical_views.upload_medical_document, name='upload_medical_document'),
    path('medico/chat-claude/', medical_views.chat_with_claude, name='chat_with_claude'),
    path('medico/documento/<int:document_id>/', medical_views.medical_document_detail, name='medical_document_detail'),
    path('medico/permiso/<int:leave_id>/', medical_views.medical_leave_detail, name='medical_leave_detail'),
    path('medico/historial/', medical_views.medical_history, name='medical_history'),
    path('medico/calificar/', medical_views.rate_claude_response, name='rate_claude_response'),
    
    # Dashboard Médico para RRHH
    path('medico/rrhh/', medical_views.hr_medical_dashboard, name='hr_medical_dashboard'),
    path('medico/rrhh/aprobar/<int:leave_id>/', medical_views.approve_medical_leave, name='approve_medical_leave'),
    
    # Acciones Rápidas - Dashboard RRHH
    path('medico/rrhh/aprobacion-masiva/', medical_views.bulk_approve_leaves, name='bulk_approve_leaves'),
    path('medico/rrhh/generar-reporte/', medical_views.generate_medical_report, name='generate_medical_report'),
    path('medico/rrhh/exportar-datos/', medical_views.export_medical_data, name='export_medical_data'),
    path('medico/rrhh/configurar-ia/', medical_views.configure_claude_ai, name='configure_claude_ai'),
]
