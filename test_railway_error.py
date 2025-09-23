#!/usr/bin/env python
"""
Test para identificar el error 500 en Railway
"""
import os
import django
import traceback

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')

try:
    django.setup()
    print("✅ Django setup exitoso")
    
    # Test de configuración
    from django.conf import settings
    print(f"✅ DEBUG: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"✅ CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'No configurado')}")
    
    # Test de base de datos
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Conexión a base de datos exitosa")
    
    # Test de URLs
    from django.urls import reverse
    try:
        login_url = reverse('login')
        print(f"✅ URL login: {login_url}")
    except Exception as e:
        print(f"❌ Error en URL login: {e}")
    
    # Test de usuario admin
    from django.contrib.auth.models import User
    admin_user = User.objects.get(username='admin')
    print(f"✅ Usuario admin encontrado: {admin_user.username}")
    
    # Test de autenticación
    from django.contrib.auth import authenticate
    auth_user = authenticate(username='admin', password='admin123')
    print(f"✅ Autenticación: {'OK' if auth_user else 'FALLO'}")
    
    # Test de vista de login
    from django.test import Client
    client = Client()
    response = client.get('/login/')
    print(f"✅ GET /login/: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Error en login: {response.content.decode()[:500]}")
    
except Exception as e:
    print(f"❌ ERROR CRÍTICO: {e}")
    print("📋 TRACEBACK:")
    traceback.print_exc()
