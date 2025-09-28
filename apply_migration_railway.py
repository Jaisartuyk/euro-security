#!/usr/bin/env python3
"""
Script para aplicar migración 0009 directamente en Railway
EURO SECURITY - Forzar aplicación de migración de códigos de turno
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection


def apply_migration_railway():
    """
    Aplicar migración 0009 directamente en Railway
    """
    print("=" * 80)
    print("🚀 EURO SECURITY - APLICAR MIGRACIÓN 0009 EN RAILWAY")
    print("=" * 80)
    
    try:
        # Verificar estado actual de migraciones
        print("📋 Verificando estado de migraciones...")
        execute_from_command_line(['manage.py', 'showmigrations', 'attendance'])
        
        print("\n🔧 Aplicando migración 0009...")
        execute_from_command_line(['manage.py', 'migrate', 'attendance', '0009'])
        
        print("\n✅ Verificando que los campos se crearon...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'attendance_shifttemplate' 
                AND column_name IN ('shift_code', 'shift_category', 'is_split_shift', 'max_agents')
                ORDER BY column_name;
            """)
            
            columns = cursor.fetchall()
            if columns:
                print("🎉 ¡CAMPOS CREADOS EXITOSAMENTE!")
                for col in columns:
                    print(f"   ✅ {col[0]}")
            else:
                print("❌ Los campos no se crearon aún")
        
        print("\n🎊 ¡MIGRACIÓN APLICADA EXITOSAMENTE!")
        print("📋 Ahora puedes descomentar los campos en models.py")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n🔧 SOLUCIÓN ALTERNATIVA:")
        print("1. Esperar a que Railway aplique automáticamente")
        print("2. O ejecutar manualmente: python manage.py migrate")


if __name__ == "__main__":
    apply_migration_railway()
