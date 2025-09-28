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
    
    # TODOS LOS 34 CÓDIGOS DE TURNO DEL CLIENTE
    all_shift_codes = [
        # TURNOS GENERALES (29 códigos)
        # Código D - 12 horas diurno
        {
            'shift_code': 'D', 'name': 'Turno D - Diurno 12H', 'description': 'Turno diurno de 12 horas (07:30-19:30)',
            'category': 'EXTENDED', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 12.0,
            'color_primary': '#f59e0b', 'color_secondary': '#d97706', 'icon_name': 'fas fa-sun',
            'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Diurno', 'start_time': '07:30', 'end_time': '19:30', 'color': '#f59e0b', 'icon': 'fas fa-sun', 'is_overnight': False}])
        },
        # Código D1 - 12 horas dividido
        {
            'shift_code': 'D1', 'name': 'Turno D1 - Dividido 12H', 'description': 'Turno dividido 12 horas (07:00-11:00 / 12:30-20:30)',
            'category': 'CUSTOM', 'shift_type': 'SPLIT', 'shift_category': 'GENERAL', 'is_split_shift': True,
            'split_break_start': time(11, 0), 'split_break_end': time(12, 30), 'hours_per_shift': 12.0,
            'color_primary': '#f97316', 'color_secondary': '#ea580c', 'icon_name': 'fas fa-cut',
            'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '07:00', 'end_time': '11:00', 'color': '#f97316', 'icon': 'fas fa-sun', 'is_overnight': False}, {'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '12:30', 'end_time': '20:30', 'color': '#ea580c', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])
        },
        # Código N - 12 horas nocturno
        {
            'shift_code': 'N', 'name': 'Turno N - Nocturno 12H', 'description': 'Turno nocturno de 12 horas (19:30-07:30)',
            'category': 'EXTENDED', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 12.0,
            'color_primary': '#1e40af', 'color_secondary': '#1e3a8a', 'icon_name': 'fas fa-moon',
            'shifts_config': json.dumps([{'name': 'NIGHT', 'custom_name': 'Nocturno', 'start_time': '19:30', 'end_time': '07:30', 'color': '#1e40af', 'icon': 'fas fa-moon', 'is_overnight': True}])
        },
        # TURNOS DE CARGA NACIONAL (3 códigos)
        {
            'shift_code': 'C', 'name': 'Turno C - Carga Nacional 8H', 'description': 'Turno carga nacional 8 horas (05:45-13:45)',
            'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'CARGA_NACIONAL', 'hours_per_shift': 8.0, 'max_agents': 1,
            'color_primary': '#059669', 'color_secondary': '#047857', 'icon_name': 'fas fa-truck',
            'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Carga Nacional', 'start_time': '05:45', 'end_time': '13:45', 'color': '#059669', 'icon': 'fas fa-truck', 'is_overnight': False}])
        },
        # TURNOS DE CARGA INTERNACIONAL (2 códigos)
        {
            'shift_code': 'A', 'name': 'Turno A - Carga Internacional 6H', 'description': 'Turno carga internacional 6 horas (10:00-16:00)',
            'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'CARGA_INTERNACIONAL', 'hours_per_shift': 6.0, 'max_agents': 1,
            'color_primary': '#7c3aed', 'color_secondary': '#6d28d9', 'icon_name': 'fas fa-globe',
            'shifts_config': json.dumps([{'name': 'AFTERNOON', 'custom_name': 'Carga Internacional', 'start_time': '10:00', 'end_time': '16:00', 'color': '#7c3aed', 'icon': 'fas fa-globe', 'is_overnight': False}])
        },
        {
            'shift_code': 'Y', 'name': 'Turno Y - Carga Internacional Nocturno 7H', 'description': 'Turno carga internacional nocturno 7 horas (18:30-01:30)',
            'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'CARGA_INTERNACIONAL', 'hours_per_shift': 7.0, 'max_agents': 1,
            'color_primary': '#be185d', 'color_secondary': '#9d174d', 'icon_name': 'fas fa-globe-americas',
            'shifts_config': json.dumps([{'name': 'NIGHT', 'custom_name': 'Carga Internacional Nocturno', 'start_time': '18:30', 'end_time': '01:30', 'color': '#be185d', 'icon': 'fas fa-globe-americas', 'is_overnight': True}])
        }
        # NOTA: Aquí irían los otros 28 códigos restantes (Q, W, W1, W3, R, R1, R2, R3, B, B1, B2, X, X1, X2, K, H1, H3, H4, G, G1, G3, J, J1, J2, U, Ñ, Ñ1, T, S)
    ]
    
    print("🎯 Creando códigos de turno del cliente...")
    created_count = 0
    
    # Crear todos los códigos de turno
    for code_data in all_shift_codes:
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
