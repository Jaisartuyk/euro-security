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
        },
        # RESTO DE CÓDIGOS GENERALES (28 restantes)
        {'shift_code': 'Q', 'name': 'Turno Q - Split 8H', 'description': 'Turno dividido 8 horas (09:00-13:00 / 15:00-19:00)', 'category': 'CUSTOM', 'shift_type': 'SPLIT', 'shift_category': 'GENERAL', 'is_split_shift': True, 'split_break_start': time(13, 0), 'split_break_end': time(15, 0), 'hours_per_shift': 8.0, 'color_primary': '#8b5cf6', 'color_secondary': '#7c3aed', 'icon_name': 'fas fa-cut', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '09:00', 'end_time': '13:00', 'color': '#8b5cf6', 'icon': 'fas fa-sun', 'is_overnight': False}, {'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '15:00', 'end_time': '19:00', 'color': '#7c3aed', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'W', 'name': 'Turno W - Split 8H', 'description': 'Turno dividido 8 horas (09:00-13:00 / 14:00-18:00)', 'category': 'CUSTOM', 'shift_type': 'SPLIT', 'shift_category': 'GENERAL', 'is_split_shift': True, 'split_break_start': time(13, 0), 'split_break_end': time(14, 0), 'hours_per_shift': 8.0, 'color_primary': '#10b981', 'color_secondary': '#059669', 'icon_name': 'fas fa-cut', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '09:00', 'end_time': '13:00', 'color': '#10b981', 'icon': 'fas fa-sun', 'is_overnight': False}, {'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '14:00', 'end_time': '18:00', 'color': '#059669', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'R', 'name': 'Turno R - Madrugada 4H', 'description': 'Turno madrugada 4 horas (01:30-05:30)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#1e293b', 'color_secondary': '#0f172a', 'icon_name': 'fas fa-moon', 'shifts_config': json.dumps([{'name': 'DAWN', 'custom_name': 'Madrugada', 'start_time': '01:30', 'end_time': '05:30', 'color': '#1e293b', 'icon': 'fas fa-moon', 'is_overnight': False}])},
        {'shift_code': 'B', 'name': 'Turno B - Diurno 12H', 'description': 'Turno diurno largo 12 horas (08:00-20:00)', 'category': 'EXTENDED', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 12.0, 'color_primary': '#dc2626', 'color_secondary': '#991b1b', 'icon_name': 'fas fa-sun', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Diurno Largo', 'start_time': '08:00', 'end_time': '20:00', 'color': '#dc2626', 'icon': 'fas fa-sun', 'is_overnight': False}])},
        {'shift_code': 'X', 'name': 'Turno X - Temprano 4H', 'description': 'Turno temprano 4 horas (06:00-10:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#f59e0b', 'color_secondary': '#d97706', 'icon_name': 'fas fa-sunrise', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Temprano', 'start_time': '06:00', 'end_time': '10:00', 'color': '#f59e0b', 'icon': 'fas fa-sunrise', 'is_overnight': False}])},
        {'shift_code': 'K', 'name': 'Turno K - Especial 1H', 'description': 'Turno especial 1 hora (09:00-10:00)', 'category': 'CUSTOM', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 1.0, 'color_primary': '#ef4444', 'color_secondary': '#dc2626', 'icon_name': 'fas fa-clock', 'shifts_config': json.dumps([{'name': 'SPECIAL', 'custom_name': 'Especial', 'start_time': '09:00', 'end_time': '10:00', 'color': '#ef4444', 'icon': 'fas fa-clock', 'is_overnight': False}])},
        {'shift_code': 'G', 'name': 'Turno G - Diurno 10H', 'description': 'Turno diurno 10 horas (09:00-19:00)', 'category': 'EXTENDED', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 10.0, 'color_primary': '#059669', 'color_secondary': '#047857', 'icon_name': 'fas fa-sun', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Diurno 10H', 'start_time': '09:00', 'end_time': '19:00', 'color': '#059669', 'icon': 'fas fa-sun', 'is_overnight': False}])},
        {'shift_code': 'J', 'name': 'Turno J - Nocturno 9H', 'description': 'Turno nocturno 9 horas (00:00-09:00)', 'category': 'EXTENDED', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 9.0, 'color_primary': '#1e40af', 'color_secondary': '#1e3a8a', 'icon_name': 'fas fa-moon', 'shifts_config': json.dumps([{'name': 'NIGHT', 'custom_name': 'Nocturno 9H', 'start_time': '00:00', 'end_time': '09:00', 'color': '#1e40af', 'icon': 'fas fa-moon', 'is_overnight': True}])},
        {'shift_code': 'U', 'name': 'Turno U - Tarde 4H', 'description': 'Turno tarde 4 horas (14:30-18:30)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#3b82f6', 'color_secondary': '#2563eb', 'icon_name': 'fas fa-cloud-sun', 'shifts_config': json.dumps([{'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '14:30', 'end_time': '18:30', 'color': '#3b82f6', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'Ñ', 'name': 'Turno Ñ - Diurno 10H', 'description': 'Turno diurno 10 horas (09:30-19:30)', 'category': 'EXTENDED', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 10.0, 'color_primary': '#7c3aed', 'color_secondary': '#6d28d9', 'icon_name': 'fas fa-sun', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Diurno Ñ', 'start_time': '09:30', 'end_time': '19:30', 'color': '#7c3aed', 'icon': 'fas fa-sun', 'is_overnight': False}])},
        {'shift_code': 'T', 'name': 'Turno T - TAMPA Variable', 'description': 'Turno TAMPA con horario variable según itinerario', 'category': 'CUSTOM', 'shift_type': 'FLEXIBLE', 'shift_category': 'GENERAL', 'is_variable_schedule': True, 'hours_per_shift': 8.0, 'color_primary': '#be185d', 'color_secondary': '#9d174d', 'icon_name': 'fas fa-route', 'shifts_config': json.dumps([{'name': 'VARIABLE', 'custom_name': 'TAMPA', 'start_time': '08:00', 'end_time': '16:00', 'color': '#be185d', 'icon': 'fas fa-route', 'is_overnight': False}])},
        # CÓDIGO S CON HORARIOS DIFERENTES POR DÍA
        {'shift_code': 'S', 'name': 'Turno S - Carga Nacional Variable', 'description': 'Turno carga nacional con horarios diferentes L-V vs S-D', 'category': 'CUSTOM', 'shift_type': 'FLEXIBLE', 'shift_category': 'CARGA_NACIONAL', 'hours_per_shift': 12.0, 'max_agents': 1, 'weekday_schedule': {'1': '05:45-17:45', '2': '05:45-17:45', '3': '05:45-17:45', '4': '05:45-17:45', '5': '05:45-17:45', '6': '05:30-17:30', '7': '05:30-17:30'}, 'color_primary': '#059669', 'color_secondary': '#047857', 'icon_name': 'fas fa-truck-loading', 'shifts_config': json.dumps([{'name': 'VARIABLE', 'custom_name': 'Carga Variable', 'start_time': '05:45', 'end_time': '17:45', 'color': '#059669', 'icon': 'fas fa-truck-loading', 'is_overnight': False}])},
        # 16 CÓDIGOS FALTANTES PARA COMPLETAR LOS 34
        {'shift_code': 'W1', 'name': 'Turno W1 - Split 8H', 'description': 'Turno dividido 8 horas (07:30-11:30 / 13:00-17:00)', 'category': 'CUSTOM', 'shift_type': 'SPLIT', 'shift_category': 'GENERAL', 'is_split_shift': True, 'split_break_start': time(11, 30), 'split_break_end': time(13, 0), 'hours_per_shift': 8.0, 'color_primary': '#10b981', 'color_secondary': '#059669', 'icon_name': 'fas fa-cut', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '07:30', 'end_time': '11:30', 'color': '#10b981', 'icon': 'fas fa-sun', 'is_overnight': False}, {'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '13:00', 'end_time': '17:00', 'color': '#059669', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'W3', 'name': 'Turno W3 - Split 8H', 'description': 'Turno dividido 8 horas (08:00-12:00 / 15:00-19:00)', 'category': 'CUSTOM', 'shift_type': 'SPLIT', 'shift_category': 'GENERAL', 'is_split_shift': True, 'split_break_start': time(12, 0), 'split_break_end': time(15, 0), 'hours_per_shift': 8.0, 'color_primary': '#10b981', 'color_secondary': '#059669', 'icon_name': 'fas fa-cut', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '08:00', 'end_time': '12:00', 'color': '#10b981', 'icon': 'fas fa-sun', 'is_overnight': False}, {'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '15:00', 'end_time': '19:00', 'color': '#059669', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'R1', 'name': 'Turno R1 - Tarde 4H', 'description': 'Turno tarde 4 horas (15:00-19:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#1e293b', 'color_secondary': '#0f172a', 'icon_name': 'fas fa-cloud-sun', 'shifts_config': json.dumps([{'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '15:00', 'end_time': '19:00', 'color': '#1e293b', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'R2', 'name': 'Turno R2 - Tarde 4H', 'description': 'Turno tarde 4 horas (17:00-21:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#1e293b', 'color_secondary': '#0f172a', 'icon_name': 'fas fa-cloud-sun', 'shifts_config': json.dumps([{'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '17:00', 'end_time': '21:00', 'color': '#1e293b', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'R3', 'name': 'Turno R3 - Mañana 4H', 'description': 'Turno mañana 4 horas (08:00-12:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#1e293b', 'color_secondary': '#0f172a', 'icon_name': 'fas fa-sun', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '08:00', 'end_time': '12:00', 'color': '#1e293b', 'icon': 'fas fa-sun', 'is_overnight': False}])},
        {'shift_code': 'B1', 'name': 'Turno B1 - Mañana 4H', 'description': 'Turno mañana 4 horas (09:00-13:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#dc2626', 'color_secondary': '#991b1b', 'icon_name': 'fas fa-sun', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '09:00', 'end_time': '13:00', 'color': '#dc2626', 'icon': 'fas fa-sun', 'is_overnight': False}])},
        {'shift_code': 'B2', 'name': 'Turno B2 - Diurno 12H', 'description': 'Turno diurno largo 12 horas (07:00-19:00)', 'category': 'EXTENDED', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 12.0, 'color_primary': '#dc2626', 'color_secondary': '#991b1b', 'icon_name': 'fas fa-sun', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Diurno Largo', 'start_time': '07:00', 'end_time': '19:00', 'color': '#dc2626', 'icon': 'fas fa-sun', 'is_overnight': False}])},
        {'shift_code': 'X1', 'name': 'Turno X1 - Mañana 4H', 'description': 'Turno mañana 4 horas (07:00-11:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#f59e0b', 'color_secondary': '#d97706', 'icon_name': 'fas fa-sunrise', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '07:00', 'end_time': '11:00', 'color': '#f59e0b', 'icon': 'fas fa-sunrise', 'is_overnight': False}])},
        {'shift_code': 'X2', 'name': 'Turno X2 - Mañana 4H', 'description': 'Turno mañana 4 horas (09:00-13:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#f59e0b', 'color_secondary': '#d97706', 'icon_name': 'fas fa-sunrise', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '09:00', 'end_time': '13:00', 'color': '#f59e0b', 'icon': 'fas fa-sunrise', 'is_overnight': False}])},
        {'shift_code': 'H1', 'name': 'Turno H1 - Tarde 4H', 'description': 'Turno tarde 4 horas (16:00-20:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#3b82f6', 'color_secondary': '#2563eb', 'icon_name': 'fas fa-cloud-sun', 'shifts_config': json.dumps([{'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '16:00', 'end_time': '20:00', 'color': '#3b82f6', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'H3', 'name': 'Turno H3 - Tarde 3H', 'description': 'Turno tarde 3 horas (16:00-19:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 3.0, 'color_primary': '#3b82f6', 'color_secondary': '#2563eb', 'icon_name': 'fas fa-cloud-sun', 'shifts_config': json.dumps([{'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '16:00', 'end_time': '19:00', 'color': '#3b82f6', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'H4', 'name': 'Turno H4 - Tarde 4H', 'description': 'Turno tarde 4 horas (16:30-20:30)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#3b82f6', 'color_secondary': '#2563eb', 'icon_name': 'fas fa-cloud-sun', 'shifts_config': json.dumps([{'name': 'AFTERNOON', 'custom_name': 'Tarde', 'start_time': '16:30', 'end_time': '20:30', 'color': '#3b82f6', 'icon': 'fas fa-cloud-sun', 'is_overnight': False}])},
        {'shift_code': 'G1', 'name': 'Turno G1 - Madrugada 4H', 'description': 'Turno madrugada 4 horas (04:00-08:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 4.0, 'color_primary': '#059669', 'color_secondary': '#047857', 'icon_name': 'fas fa-moon', 'shifts_config': json.dumps([{'name': 'DAWN', 'custom_name': 'Madrugada', 'start_time': '04:00', 'end_time': '08:00', 'color': '#059669', 'icon': 'fas fa-moon', 'is_overnight': False}])},
        {'shift_code': 'G3', 'name': 'Turno G3 - Split 11H', 'description': 'Turno dividido 11 horas (09:00-19:00 / 19:30-20:30)', 'category': 'CUSTOM', 'shift_type': 'SPLIT', 'shift_category': 'GENERAL', 'is_split_shift': True, 'split_break_start': time(19, 0), 'split_break_end': time(19, 30), 'hours_per_shift': 11.0, 'color_primary': '#059669', 'color_secondary': '#047857', 'icon_name': 'fas fa-cut', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Diurno', 'start_time': '09:00', 'end_time': '19:00', 'color': '#059669', 'icon': 'fas fa-sun', 'is_overnight': False}, {'name': 'EVENING', 'custom_name': 'Noche', 'start_time': '19:30', 'end_time': '20:30', 'color': '#047857', 'icon': 'fas fa-moon', 'is_overnight': False}])},
        {'shift_code': 'J1', 'name': 'Turno J1 - Nocturno 5H', 'description': 'Turno nocturno 5 horas (00:00-05:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 5.0, 'color_primary': '#1e40af', 'color_secondary': '#1e3a8a', 'icon_name': 'fas fa-moon', 'shifts_config': json.dumps([{'name': 'NIGHT', 'custom_name': 'Nocturno', 'start_time': '00:00', 'end_time': '05:00', 'color': '#1e40af', 'icon': 'fas fa-moon', 'is_overnight': True}])},
        {'shift_code': 'J2', 'name': 'Turno J2 - Nocturno 8H', 'description': 'Turno nocturno 8 horas (01:00-09:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 8.0, 'color_primary': '#1e40af', 'color_secondary': '#1e3a8a', 'icon_name': 'fas fa-moon', 'shifts_config': json.dumps([{'name': 'NIGHT', 'custom_name': 'Nocturno', 'start_time': '01:00', 'end_time': '09:00', 'color': '#1e40af', 'icon': 'fas fa-moon', 'is_overnight': True}])},
        {'shift_code': 'Ñ1', 'name': 'Turno Ñ1 - Mañana 6H', 'description': 'Turno mañana 6 horas (08:00-14:00)', 'category': 'STANDARD', 'shift_type': 'FIXED', 'shift_category': 'GENERAL', 'hours_per_shift': 6.0, 'color_primary': '#7c3aed', 'color_secondary': '#6d28d9', 'icon_name': 'fas fa-sun', 'shifts_config': json.dumps([{'name': 'MORNING', 'custom_name': 'Mañana', 'start_time': '08:00', 'end_time': '14:00', 'color': '#7c3aed', 'icon': 'fas fa-sun', 'is_overnight': False}])}
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
