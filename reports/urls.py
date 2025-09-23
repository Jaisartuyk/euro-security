from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_dashboard, name='dashboard'),
    path('empleados/', views.employee_reports, name='employees'),
    path('departamentos/', views.department_reports, name='departments'),
    path('puestos/', views.position_reports, name='positions'),
    path('nomina/', views.payroll_reports, name='payroll'),
    path('analiticos/', views.analytics_reports, name='analytics'),
    path('api/', views.reports_api, name='api'),
]
