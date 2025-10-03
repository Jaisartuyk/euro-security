"""
URLs para el Sistema de Control de Calidad
"""
from django.urls import path
from . import views

app_name = 'quality_control'

urlpatterns = [
    # Dashboard principal
    path('', views.quality_dashboard, name='dashboard'),
    
    # Matriz de riesgos
    path('matriz/', views.risk_matrix, name='risk_matrix'),
    
    # Riesgos
    path('riesgos/', views.risk_list, name='risk_list'),
    path('riesgos/<int:risk_id>/', views.risk_detail, name='risk_detail'),
    
    # Medidas de control
    path('medidas/', views.control_measures_list, name='control_measures'),
    
    # Incidentes
    path('incidentes/', views.incidents_list, name='incidents'),
    
    # Reportes
    path('reportes/', views.reports, name='reports'),
]
