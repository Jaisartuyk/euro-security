#!/usr/bin/env python
"""
Forzar uso de SQLite y crear tablas
"""
import os
import django

# Remover DATABASE_URL para forzar SQLite
os.environ.pop('DATABASE_URL', None)
os.environ.pop('DATABASE_PUBLIC_URL', None)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User

def setup_sqlite():
    print("🗄️ CONFIGURANDO SQLITE TEMPORAL...")
    
    # Ejecutar migraciones
    print("1️⃣ Aplicando migraciones...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Crear superusuario
    print("2️⃣ Creando superusuario...")
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Usuario admin ya existe: {admin_user.username}")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='jairo1991st@hotmail.com',
            password='admin123'
        )
        print(f"✅ Usuario admin creado: {admin_user.username}")
    
    # Establecer contraseña conocida
    admin_user.set_password('admin123')
    admin_user.save()
    print("✅ Contraseña admin establecida: admin123")
    
    print("\n🎯 SQLITE CONFIGURADO:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   URL: https://euro-security-production.up.railway.app/login/")
    print("\n⚠️ NOTA: Usando SQLite temporal hasta que PostgreSQL funcione")

if __name__ == '__main__':
    setup_sqlite()
