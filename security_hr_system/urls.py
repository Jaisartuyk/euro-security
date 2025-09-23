"""
URL configuration for security_hr_system project.
Sistema de Gestión de Personal - TV Services
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from core.views import custom_logout

# Personalizar el admin
admin.site.site_header = "EURO SECURITY - Administración"
admin.site.site_title = "EURO SECURITY HR"
admin.site.index_title = "Sistema de Gestión de Personal"

def redirect_to_dashboard(request):
    """Redirigir la raíz al dashboard"""
    return redirect('dashboard:home')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_dashboard, name='home'),
    path('dashboard/', include('dashboard.urls')),
    path('empleados/', include('employees.urls')),
    path('departamentos/', include('departments.urls')),
    path('puestos/', include('positions.urls')),
    path('reportes/', include('reports.urls')),
    path('asistencia/', include('attendance.urls')),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)
