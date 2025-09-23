#!/usr/bin/env python
"""
Test de conexión a base de datos
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.conf import settings
from django.db import connection

def test_database_connection():
    print("🗄️ TEST DE CONEXIÓN A BASE DE DATOS")
    print("=" * 50)
    
    # Mostrar configuración
    db_config = settings.DATABASES['default']
    print(f"Engine: {db_config['ENGINE']}")
    
    if 'postgresql' in db_config['ENGINE']:
        print(f"Host: {db_config.get('HOST', 'N/A')}")
        print(f"Port: {db_config.get('PORT', 'N/A')}")
        print(f"Database: {db_config.get('NAME', 'N/A')}")
        print(f"User: {db_config.get('USER', 'N/A')}")
    else:
        print(f"SQLite File: {db_config.get('NAME', 'N/A')}")
    
    # Test de conexión
    try:
        with connection.cursor() as cursor:
            if 'postgresql' in db_config['ENGINE']:
                cursor.execute("SELECT version(), current_database()")
                result = cursor.fetchone()
                print(f"✅ PostgreSQL conectado: {result[1]}")
                print(f"✅ Versión: {result[0][:50]}...")
            else:
                cursor.execute("SELECT sqlite_version()")
                result = cursor.fetchone()
                print(f"✅ SQLite conectado: {result[0]}")
                
            # Verificar si existen tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'" if 'sqlite' in db_config['ENGINE'] else "SELECT tablename FROM pg_tables WHERE schemaname='public'")
            tables = cursor.fetchall()
            print(f"✅ Tablas encontradas: {len(tables)}")
            
            if len(tables) > 0:
                print("📋 Primeras 5 tablas:")
                for table in tables[:5]:
                    print(f"   - {table[0]}")
            else:
                print("⚠️ No hay tablas - necesitas ejecutar migrate")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"❌ Tipo de error: {type(e).__name__}")

if __name__ == '__main__':
    test_database_connection()
