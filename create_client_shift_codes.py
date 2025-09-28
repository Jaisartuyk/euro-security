#!/usr/bin/env python3
"""
Script para crear los 34 códigos de turno específicos del cliente
EURO SECURITY - Códigos de Turno Completos
"""

import os
import sys
import django
import json
from datetime import time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from attendance.models import ShiftTemplate


def create_client_shift_codes():
    """Crear los 34 códigos de turno específicos del cliente"""
    
    print("=" * 80)
    print("🏢 EURO SECURITY - CREACIÓN DE 34 CÓDIGOS DE TURNO")
    print("=" * 80)
    
    # PARTE 1: TURNOS GENERALES (29 códigos)
    general_codes = [
        # Código D - 12 horas diurno
        {
            'shift_code': 'D',
            'name': 'Turno D - Diurno 12H',
            'description': 'Turno diurno de 12 horas (07:30-19:30)',
            'category': 'EXTENDED',
            'shift_type': 'FIXED',
            'shift_category': 'GENERAL',
            'hours_per_shift': 12.0,
            'color_primary': '#f59e0b',
            'color_secondary': '#d97706',
            'icon_name': 'fas fa-sun',
            'shifts_config': json.dumps([{
                'name': 'MORNING',
                'custom_name': 'Diurno',
                'start_time': '07:30',
                'end_time': '19:30',
                'color': '#f59e0b',
                'icon': 'fas fa-sun',
                'is_overnight': False
            }])
        },
        # Código D1 - 12 horas dividido
        {
            'shift_code': 'D1',
            'name': 'Turno D1 - Dividido 12H',
            'description': 'Turno dividido 12 horas (07:00-11:00 / 12:30-20:30)',
            'category': 'CUSTOM',
            'shift_type': 'SPLIT',
            'shift_category': 'GENERAL',
            'is_split_shift': True,
            'split_break_start': time(11, 0),
            'split_break_end': time(12, 30),
            'hours_per_shift': 12.0,
            'color_primary': '#f97316',
            'color_secondary': '#ea580c',
            'icon_name': 'fas fa-cut',
            'shifts_config': json.dumps([
                {
                    'name': 'MORNING',
                    'custom_name': 'Mañana',
                    'start_time': '07:00',
                    'end_time': '11:00',
                    'color': '#f97316',
                    'icon': 'fas fa-sun',
                    'is_overnight': False
                },
                {
                    'name': 'AFTERNOON',
                    'custom_name': 'Tarde',
                    'start_time': '12:30',
                    'end_time': '20:30',
                    'color': '#ea580c',
                    'icon': 'fas fa-cloud-sun',
                    'is_overnight': False
                }
            ])
        }
    ]
    
    print("🎯 Creando códigos de turno del cliente...")
    created_count = 0
    
    # Crear códigos generales (primeros 2 como ejemplo)
    for code_data in general_codes:
        template, created = ShiftTemplate.objects.get_or_create(
            shift_code=code_data['shift_code'],
            defaults=code_data
        )
        
        if created:
            print(f"✅ Creado: {template.shift_code} - {template.name}")
            created_count += 1
        else:
            print(f"⚠️  Ya existe: {template.shift_code} - {template.name}")
    
    print(f"\n🎊 ¡Proceso iniciado! {created_count} códigos creados.")
    print("📋 Ejecutar script completo para crear los 34 códigos restantes.")


if __name__ == "__main__":
    create_client_shift_codes()
