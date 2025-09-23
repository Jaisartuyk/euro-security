#!/usr/bin/env python
"""
Crear tablas en PostgreSQL de Railway
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User

def create_tables_and_user():
    print("🗄️ CREANDO TABLAS EN POSTGRESQL...")
    
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
    
    # Verificar conexión a base de datos
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), version()")
        db_info = cursor.fetchone()
        print(f"✅ Conectado a: {db_info[0]}")
        print(f"✅ PostgreSQL: {db_info[1][:50]}...")
    
    print("\n🎯 CONFIGURACIÓN COMPLETADA:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   URL: https://euro-security-production.up.railway.app/login/")

if __name__ == '__main__':
    create_tables_and_user()
