#!/usr/bin/env python
"""
Test completo del sistema de login
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.test import Client
from django.urls import reverse

def test_login_system():
    print("🔍 TEST COMPLETO DEL SISTEMA DE LOGIN")
    print("=" * 60)
    
    # 1. Verificar usuarios
    print("1️⃣ VERIFICANDO USUARIOS:")
    admin_user = User.objects.get(username='admin')
    jairo_user = User.objects.get(username='jairo')
    
    print(f"   ✅ Admin: {admin_user.username} - Activo: {admin_user.is_active}")
    print(f"   ✅ Jairo: {jairo_user.username} - Activo: {jairo_user.is_active}")
    
    # 2. Test de autenticación
    print("\n2️⃣ TEST DE AUTENTICACIÓN:")
    auth_admin = authenticate(username='admin', password='admin123')
    print(f"   Admin con admin123: {'✅ OK' if auth_admin else '❌ FALLO'}")
    
    # 3. Test del cliente Django
    print("\n3️⃣ TEST DEL CLIENTE DJANGO:")
    client = Client()
    
    # Test GET login page
    try:
        login_url = reverse('login')
        response = client.get(login_url)
        print(f"   GET /login/: {response.status_code} {'✅ OK' if response.status_code == 200 else '❌ ERROR'}")
    except Exception as e:
        print(f"   GET /login/: ❌ ERROR - {e}")
    
    # Test POST login
    try:
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        response = client.post(login_url, login_data)
        print(f"   POST login admin: {response.status_code}")
        if response.status_code == 302:
            print(f"   ✅ Redirect a: {response.url}")
        elif response.status_code == 200:
            print("   ⚠️ Permaneció en login (posible error)")
        else:
            print(f"   ❌ Error inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   POST login: ❌ ERROR - {e}")
    
    # 4. Verificar configuración
    print("\n4️⃣ CONFIGURACIÓN:")
    from django.conf import settings
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print(f"   LOGIN_URL: {getattr(settings, 'LOGIN_URL', '/accounts/login/')}")
    print(f"   LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', '/accounts/profile/')}")
    
    # 5. URLs disponibles
    print("\n5️⃣ URLs PRINCIPALES:")
    from django.urls import get_resolver
    resolver = get_resolver()
    
    important_urls = ['login', 'dashboard', 'home']
    for url_name in important_urls:
        try:
            url = reverse(url_name)
            print(f"   ✅ {url_name}: {url}")
        except:
            print(f"   ❌ {url_name}: No encontrada")

if __name__ == '__main__':
    test_login_system()
