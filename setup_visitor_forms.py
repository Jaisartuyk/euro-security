#!/usr/bin/env python
"""
Script para ejecutar el comando de crear formularios de visitantes
Se ejecuta una sola vez y luego se puede eliminar
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

# Ejecutar el comando
from django.core.management import call_command

print("🚀 Creando formularios de visitantes...")
call_command('create_visitor_forms')
print("✅ ¡Formularios creados exitosamente!")
