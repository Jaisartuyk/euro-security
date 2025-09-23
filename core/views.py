"""
Vistas centrales del sistema
"""
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponse


def custom_logout(request):
    """Vista personalizada de logout que acepta GET y POST"""
    if request.user.is_authenticated:
        user_name = request.user.username
        logout(request)
        messages.success(request, f'Has cerrado sesión exitosamente. ¡Hasta pronto, {user_name}!')
    
    return redirect('login')


def health_check(request):
    """Vista simple para verificar que el servidor esté funcionando"""
    return HttpResponse("Sistema EURO SECURITY funcionando correctamente", content_type="text/plain")
