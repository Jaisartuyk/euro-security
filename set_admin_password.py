#!/usr/bin/env python
"""
Script para establecer contraseña conocida para admin
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.contrib.auth.models import User

def set_admin_password():
    try:
        admin_user = User.objects.get(username='admin')
        
        # Establecer contraseña conocida
        admin_user.set_password('admin123')
        admin_user.save()
        
        print("✅ Contraseña establecida exitosamente")
        print("🔑 Credenciales para login:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   URL: https://euro-security-production.up.railway.app/login/")
        
        # Verificar que el usuario puede autenticarse
        from django.contrib.auth import authenticate
        user = authenticate(username='admin', password='admin123')
        if user:
            print("✅ Autenticación verificada - Las credenciales funcionan")
        else:
            print("❌ Error en autenticación")
            
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado")

if __name__ == '__main__':
    set_admin_password()
