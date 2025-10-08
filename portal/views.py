"""
Vistas para el Portal de Aplicaciones
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


@login_required
def apps_portal(request):
    """Portal de aplicaciones - Solo para el dueño (ABRAHAM)"""
    
    # Verificar que el usuario sea ABRAHAM
    if request.user.username != 'ABRAHAM':
        return HttpResponseForbidden("No tienes permisos para acceder a esta página.")
    
    # Definir las aplicaciones
    apps = [
        {
            'nombre': 'Geomarlab SA',
            'url': 'https://geomarlab-production.up.railway.app/',
            'descripcion': 'Cría y Precría de Larvas de Camarones',
            'icono': '🦐',
            'color': '#3b82f6',  # Azul
            'color_hover': '#2563eb',
            'categoria': 'Producción'
        },
        {
            'nombre': 'Euro Security HR',
            'url': 'https://euro-security-production.up.railway.app/',
            'descripcion': 'Sistema de Recursos Humanos y Seguridad',
            'icono': '🛡️',
            'color': '#ef4444',  # Rojo
            'color_hover': '#dc2626',
            'categoria': 'Administración'
        },
    ]
    
    context = {
        'apps': apps,
        'total_apps': len(apps),
        'page_title': 'Mis Aplicaciones',
    }
    
    return render(request, 'portal/apps.html', context)
