#!/usr/bin/env python
"""
Script para verificar y crear usuario admin en EURO SECURITY
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.contrib.auth.models import User

def fix_admin_user():
    print("🔍 Verificando usuario admin...")
    
    # Verificar si existe el usuario admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario admin encontrado: {admin_user.username} ({admin_user.email})")
        print(f"   - Es superusuario: {admin_user.is_superuser}")
        print(f"   - Está activo: {admin_user.is_active}")
        print(f"   - Es staff: {admin_user.is_staff}")
        
        # Asegurar que tenga todos los permisos
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.save()
        print("✅ Permisos de admin actualizados")
        
    except User.DoesNotExist:
        print("❌ Usuario admin no encontrado. Creando nuevo usuario...")
        
        # Crear nuevo usuario admin
        admin_user = User.objects.create_superuser(
            username='admin',
            email='jairo1991st@hotmail.com',
            password='admin123'  # Contraseña temporal
        )
        print(f"✅ Usuario admin creado: {admin_user.username}")
        print("🔑 Contraseña temporal: admin123")
    
    # Verificar otros usuarios
    print("\n👥 Todos los usuarios en el sistema:")
    for user in User.objects.all():
        print(f"   - {user.username} ({user.email}) - Superuser: {user.is_superuser}")
    
    print("\n🎯 Credenciales para login:")
    print("   Username: admin")
    print("   Password: admin123 (o la que configuraste)")
    print("   URL: https://euro-security-production.up.railway.app/login/")

if __name__ == '__main__':
    fix_admin_user()
