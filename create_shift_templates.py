#!/usr/bin/env python3
"""
Script para crear plantillas de turnos predefinidas
EURO SECURITY - Configuración inicial de turnos
"""

import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from attendance.models import ShiftTemplate


def create_shift_templates():
    """Crear plantillas de turnos predefinidas"""
    
    templates = [
        {
            'name': '3 Turnos de 8 Horas (24/7)',
            'description': 'Cobertura completa 24/7 con 3 turnos de 8 horas cada uno',
            'category': 'SECURITY',
            'shift_type': 'ROTATING',
            'total_shifts_per_day': 3,
            'hours_per_shift': 8.0,
            'rotation_days': 7,
            'icon_name': 'fas fa-shield-alt',
            'color_primary': '#dc2626',
            'color_secondary': '#991b1b',
            'shifts_config': json.dumps([
                {
                    'name': 'MORNING',
                    'custom_name': 'Matutino',
                    'start_time': '06:00',
                    'end_time': '14:00',
                    'color': '#f59e0b',
                    'icon': 'fas fa-sun',
                    'is_overnight': False
                },
                {
                    'name': 'AFTERNOON',
                    'custom_name': 'Vespertino',
                    'start_time': '14:00',
                    'end_time': '22:00',
                    'color': '#3b82f6',
                    'icon': 'fas fa-cloud-sun',
                    'is_overnight': False
                },
                {
                    'name': 'NIGHT',
                    'custom_name': 'Nocturno',
                    'start_time': '22:00',
                    'end_time': '06:00',
                    'color': '#1e40af',
                    'icon': 'fas fa-moon',
                    'is_overnight': True
                }
            ]),
            'is_default': True
        },
        {
            'name': '2 Turnos de 12 Horas',
            'description': 'Cobertura 24/7 con 2 turnos extendidos de 12 horas',
            'category': 'EXTENDED',
            'shift_type': 'ROTATING',
            'total_shifts_per_day': 2,
            'hours_per_shift': 12.0,
            'rotation_days': 14,
            'icon_name': 'fas fa-clock',
            'color_primary': '#059669',
            'color_secondary': '#047857',
            'shifts_config': json.dumps([
                {
                    'name': 'MORNING',
                    'custom_name': 'Diurno',
                    'start_time': '07:00',
                    'end_time': '19:00',
                    'color': '#f59e0b',
                    'icon': 'fas fa-sun',
                    'is_overnight': False
                },
                {
                    'name': 'NIGHT',
                    'custom_name': 'Nocturno',
                    'start_time': '19:00',
                    'end_time': '07:00',
                    'color': '#1e40af',
                    'icon': 'fas fa-moon',
                    'is_overnight': True
                }
            ])
        },
        {
            'name': 'Horario de Oficina (8 hrs)',
            'description': 'Horario estándar de oficina de lunes a viernes',
            'category': 'OFFICE',
            'shift_type': 'FIXED',
            'total_shifts_per_day': 1,
            'hours_per_shift': 8.0,
            'rotation_days': 0,
            'icon_name': 'fas fa-building',
            'color_primary': '#6366f1',
            'color_secondary': '#4f46e5',
            'shifts_config': json.dumps([
                {
                    'name': 'MORNING',
                    'custom_name': 'Oficina',
                    'start_time': '08:00',
                    'end_time': '17:00',
                    'color': '#6366f1',
                    'icon': 'fas fa-briefcase',
                    'is_overnight': False
                }
            ]),
            'is_default': True
        },
        {
            'name': 'Turno Flexible (8 hrs)',
            'description': 'Horario flexible con 8 horas de trabajo',
            'category': 'STANDARD',
            'shift_type': 'FLEXIBLE',
            'total_shifts_per_day': 1,
            'hours_per_shift': 8.0,
            'rotation_days': 0,
            'icon_name': 'fas fa-user-clock',
            'color_primary': '#8b5cf6',
            'color_secondary': '#7c3aed',
            'shifts_config': json.dumps([
                {
                    'name': 'CUSTOM',
                    'custom_name': 'Flexible',
                    'start_time': '09:00',
                    'end_time': '18:00',
                    'color': '#8b5cf6',
                    'icon': 'fas fa-user-clock',
                    'is_overnight': False
                }
            ])
        },
        {
            'name': '4 Turnos de 6 Horas',
            'description': 'Cobertura 24/7 con 4 turnos cortos de 6 horas',
            'category': 'SECURITY',
            'shift_type': 'ROTATING',
            'total_shifts_per_day': 4,
            'hours_per_shift': 6.0,
            'rotation_days': 5,
            'icon_name': 'fas fa-users',
            'color_primary': '#ef4444',
            'color_secondary': '#dc2626',
            'shifts_config': json.dumps([
                {
                    'name': 'DAWN',
                    'custom_name': 'Madrugada',
                    'start_time': '00:00',
                    'end_time': '06:00',
                    'color': '#1e293b',
                    'icon': 'fas fa-moon',
                    'is_overnight': False
                },
                {
                    'name': 'MORNING',
                    'custom_name': 'Mañana',
                    'start_time': '06:00',
                    'end_time': '12:00',
                    'color': '#f59e0b',
                    'icon': 'fas fa-sun',
                    'is_overnight': False
                },
                {
                    'name': 'AFTERNOON',
                    'custom_name': 'Tarde',
                    'start_time': '12:00',
                    'end_time': '18:00',
                    'color': '#3b82f6',
                    'icon': 'fas fa-cloud-sun',
                    'is_overnight': False
                },
                {
                    'name': 'NIGHT',
                    'custom_name': 'Noche',
                    'start_time': '18:00',
                    'end_time': '00:00',
                    'color': '#1e40af',
                    'icon': 'fas fa-moon',
                    'is_overnight': False
                }
            ])
        },
        {
            'name': 'Turno Partido (4+4 hrs)',
            'description': 'Turno dividido con descanso largo en el medio',
            'category': 'CUSTOM',
            'shift_type': 'SPLIT',
            'total_shifts_per_day': 1,
            'hours_per_shift': 8.0,
            'rotation_days': 0,
            'icon_name': 'fas fa-cut',
            'color_primary': '#f97316',
            'color_secondary': '#ea580c',
            'shifts_config': json.dumps([
                {
                    'name': 'CUSTOM',
                    'custom_name': 'Mañana',
                    'start_time': '08:00',
                    'end_time': '12:00',
                    'color': '#f97316',
                    'icon': 'fas fa-sun',
                    'is_overnight': False
                },
                {
                    'name': 'CUSTOM',
                    'custom_name': 'Tarde',
                    'start_time': '16:00',
                    'end_time': '20:00',
                    'color': '#ea580c',
                    'icon': 'fas fa-cloud-sun',
                    'is_overnight': False
                }
            ])
        }
    ]
    
    print("🎯 Creando plantillas de turnos predefinidas...")
    
    created_count = 0
    for template_data in templates:
        template, created = ShiftTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        
        if created:
            print(f"✅ Creada: {template.name}")
            created_count += 1
        else:
            print(f"⚠️  Ya existe: {template.name}")
    
    print(f"\n🎊 ¡Proceso completado! {created_count} plantillas nuevas creadas.")
    print(f"📊 Total de plantillas disponibles: {ShiftTemplate.objects.count()}")


if __name__ == "__main__":
    print("=" * 60)
    print("🏢 EURO SECURITY - CONFIGURACIÓN DE TURNOS")
    print("=" * 60)
    
    try:
        create_shift_templates()
        print("\n🚀 ¡Sistema de turnos listo para usar!")
        print("💡 Los administradores ahora pueden configurar horarios desde la interfaz web")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
