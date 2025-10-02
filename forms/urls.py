from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    # Dashboard principal
    path('', views.forms_dashboard, name='dashboard'),
    
    # Formularios por categoría
    path('categoria/<int:category_id>/', views.forms_by_category, name='category'),
    
    # Vista previa y descarga de formulario
    path('preview/<int:form_id>/', views.preview_form, name='preview'),
    path('descargar/<int:form_id>/', views.download_form, name='download'),
    
    # Búsqueda
    path('buscar/', views.search_forms, name='search'),
    
    # Estadísticas (solo admin)
    path('estadisticas/', views.forms_stats, name='stats'),
    
    # ============================================================================
    # URLs PARA FORMULARIOS DINÁMICOS
    # ============================================================================
    
    # Dashboard dinámico
    path('dinamicos/', views.dynamic_forms_dashboard, name='dynamic_dashboard'),
    
    # Plantillas
    path('plantilla/<int:template_id>/', views.template_detail, name='template_detail'),
    path('plantilla/<int:template_id>/asignar/', views.assign_form, name='assign_form'),
    
    # Completar formularios
    path('completar/<int:template_id>/', views.fill_form, name='fill_form'),
    path('completar/<int:template_id>/asignacion/<int:assignment_id>/', views.fill_form, name='fill_assigned_form'),
    
    # Envíos
    path('envio/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('envio/<int:submission_id>/revisar/', views.review_submission, name='review_submission'),
    path('envio/<int:submission_id>/pdf/', views.export_submission_pdf, name='export_submission_pdf'),
]
