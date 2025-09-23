from django.urls import path
from . import views, employee_views

app_name = 'employees'

urlpatterns = [
    # Vistas administrativas
    path('', views.employee_list, name='list'),
    path('crear/', views.employee_create, name='create'),
    path('<int:pk>/', views.employee_detail, name='detail'),
    path('<int:pk>/editar/', views.employee_edit, name='edit'),
    path('<int:pk>/crear-usuario/', views.create_user_for_employee, name='create_user'),
    path('<int:pk>/resetear-password/', views.reset_user_password, name='reset_password'),
    path('api/estadisticas/', views.employee_stats_api, name='stats_api'),
    
    # Vistas para empleados (self-service)
    path('mi-perfil/', employee_views.employee_profile, name='profile'),
    path('mi-dashboard/', employee_views.employee_dashboard, name='dashboard'),
    path('mi-equipo/', employee_views.employee_team, name='team'),
    path('cambiar-password/', employee_views.employee_change_password, name='change_password'),
    path('mis-permisos/', employee_views.employee_permissions_info, name='permissions_info'),
]
