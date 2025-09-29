#!/usr/bin/env python3
"""
Script para verificar códigos de turno en Railway
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from attendance.models import ShiftTemplate

def check_shift_codes():
    """Verificar códigos de turno existentes"""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CÓDIGOS DE TURNO")
    print("=" * 60)
    
    templates = ShiftTemplate.objects.all()
    print(f"📊 Total plantillas encontradas: {templates.count()}")
    print()
    
    # Plantillas con código
    with_code = templates.exclude(shift_code__isnull=True).exclude(shift_code='')
    print(f"✅ Con código específico: {with_code.count()}")
    for t in with_code:
        print(f"   {t.shift_code}: {t.name}")
    
    print()
    
    # Plantillas sin código
    without_code = templates.filter(shift_code__isnull=True) | templates.filter(shift_code='')
    print(f"⚠️  Sin código específico: {without_code.count()}")
    for t in without_code:
        print(f"   SIN_CÓDIGO: {t.name}")
    
    print()
    print("🎯 CÓDIGOS ESPERADOS DEL CLIENTE:")
    expected_codes = ['D', 'D1', 'N', 'Q', 'W', 'W1', 'W3', 'R', 'R1', 'R2', 'R3', 
                     'B', 'B1', 'B2', 'X', 'X1', 'X2', 'K', 'H1', 'H3', 'H4', 
                     'G', 'G1', 'G3', 'J', 'J1', 'J2', 'U', 'Ñ', 'Ñ1', 'T', 
                     'C', 'S', 'A', 'Y']
    
    existing_codes = [t.shift_code for t in with_code if t.shift_code]
    missing_codes = [code for code in expected_codes if code not in existing_codes]
    
    print(f"✅ Códigos existentes: {len(existing_codes)}/34")
    print(f"❌ Códigos faltantes: {len(missing_codes)}/34")
    
    if missing_codes:
        print("📋 Códigos faltantes:", ', '.join(missing_codes))

if __name__ == "__main__":
    check_shift_codes()
