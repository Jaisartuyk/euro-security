#!/usr/bin/env python
"""
Script para debuggear problemas de login
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def debug_login():
    print("🔍 DEBUG LOGIN - EURO SECURITY")
    print("=" * 50)
    
    # Verificar usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario encontrado: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Activo: {admin_user.is_active}")
        print(f"   Staff: {admin_user.is_staff}")
        print(f"   Superuser: {admin_user.is_superuser}")
        print(f"   Último login: {admin_user.last_login}")
        
        # Probar autenticación
        print("\n🔐 Probando autenticación...")
        user = authenticate(username='admin', password='admin123')
        if user:
            print("✅ Autenticación EXITOSA")
            print(f"   Usuario autenticado: {user.username}")
        else:
            print("❌ Autenticación FALLÓ")
            
            # Probar con diferentes contraseñas
            print("\n🔍 Probando contraseñas alternativas...")
            passwords = ['admin123', 'admin', '123456', 'password']
            for pwd in passwords:
                test_user = authenticate(username='admin', password=pwd)
                if test_user:
                    print(f"✅ Contraseña correcta: {pwd}")
                    break
                else:
                    print(f"❌ Falló con: {pwd}")
        
        # Verificar configuración de Django
        print("\n⚙️ Configuración Django:")
        from django.conf import settings
        print(f"   DEBUG: {settings.DEBUG}")
        print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        print(f"   SECRET_KEY configurada: {'Sí' if settings.SECRET_KEY else 'No'}")
        
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado")
        
    # Listar todos los superusuarios
    print("\n👑 Superusuarios disponibles:")
    superusers = User.objects.filter(is_superuser=True)
    for su in superusers:
        print(f"   - {su.username} ({su.email})")

if __name__ == '__main__':
    debug_login()
