#!/usr/bin/env python
"""
Script para configurar el sistema de turnos en producción (Railway)
EURO SECURITY - Sistema de Turnos Dinámicos
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from attendance.models import ShiftTemplate


def setup_shifts_in_production():
    """
    Configura el sistema de turnos en producción
    """
    print("=" * 60)
    print("🏢 EURO SECURITY - CONFIGURACIÓN DE TURNOS EN PRODUCCIÓN")
    print("=" * 60)
    
    # Verificar que las tablas existen
    try:
        count = ShiftTemplate.objects.count()
        print(f"✅ Tablas de turnos detectadas. Plantillas existentes: {count}")
    except Exception as e:
        print(f"❌ Error: Las tablas no existen aún: {e}")
        print("⏳ Esperando a que Railway aplique las migraciones...")
        return False
    
    # Si ya hay plantillas, no crear duplicadas
    if count > 0:
        print(f"ℹ️  Ya existen {count} plantillas. No se crearán duplicadas.")
        return True
    
    print("🎯 Creando plantillas de turnos predefinidas...")
    
    # Plantillas predefinidas
    templates_data = [
        {
            'name': '3 Turnos de 8 Horas (24/7)',
            'description': 'Cobertura completa 24/7 con tres turnos de 8 horas cada uno. Ideal para seguridad y vigilancia.',
            'category': 'SECURITY',
            'shift_type': 'ROTATING',
            'total_shifts_per_day': 3,
            'hours_per_shift': 8.0,
            'rotation_days': 7,
            'icon_name': 'fas fa-shield-alt',
            'color_primary': '#dc2626',
            'color_secondary': '#991b1b',
            'shifts_config': '[{"name":"MORNING","custom_name":"Matutino","start_time":"06:00","end_time":"14:00","color":"#f59e0b","icon":"fas fa-sun"},{"name":"AFTERNOON","custom_name":"Vespertino","start_time":"14:00","end_time":"22:00","color":"#3b82f6","icon":"fas fa-cloud-sun"},{"name":"NIGHT","custom_name":"Nocturno","start_time":"22:00","end_time":"06:00","color":"#6366f1","icon":"fas fa-moon","is_overnight":true}]',
            'is_default': True
        },
        {
            'name': '2 Turnos de 12 Horas',
            'description': 'Dos turnos extendidos de 12 horas para máxima cobertura con menos cambios de personal.',
            'category': 'EXTENDED',
            'shift_type': 'ROTATING',
            'total_shifts_per_day': 2,
            'hours_per_shift': 12.0,
            'rotation_days': 14,
            'icon_name': 'fas fa-clock',
            'color_primary': '#059669',
            'color_secondary': '#047857',
            'shifts_config': '[{"name":"MORNING","custom_name":"Diurno","start_time":"07:00","end_time":"19:00","color":"#f59e0b","icon":"fas fa-sun"},{"name":"NIGHT","custom_name":"Nocturno","start_time":"19:00","end_time":"07:00","color":"#6366f1","icon":"fas fa-moon","is_overnight":true}]',
            'is_default': False
        },
        {
            'name': 'Horario de Oficina (8 hrs)',
            'description': 'Horario estándar de oficina de lunes a viernes, ideal para personal administrativo.',
            'category': 'OFFICE',
            'shift_type': 'FIXED',
            'total_shifts_per_day': 1,
            'hours_per_shift': 8.0,
            'rotation_days': 0,
            'icon_name': 'fas fa-building',
            'color_primary': '#3b82f6',
            'color_secondary': '#1e40af',
            'shifts_config': '[{"name":"MORNING","custom_name":"Oficina","start_time":"08:00","end_time":"17:00","color":"#3b82f6","icon":"fas fa-briefcase"}]',
            'is_default': False
        },
        {
            'name': 'Turno Flexible (8 hrs)',
            'description': 'Horario flexible de 8 horas que permite adaptarse a diferentes necesidades operativas.',
            'category': 'STANDARD',
            'shift_type': 'FLEXIBLE',
            'total_shifts_per_day': 1,
            'hours_per_shift': 8.0,
            'rotation_days': 0,
            'icon_name': 'fas fa-adjust',
            'color_primary': '#7c3aed',
            'color_secondary': '#5b21b6',
            'shifts_config': '[{"name":"CUSTOM","custom_name":"Flexible","start_time":"09:00","end_time":"18:00","color":"#7c3aed","icon":"fas fa-clock"}]',
            'is_default': False
        },
        {
            'name': '4 Turnos de 6 Horas',
            'description': 'Cuatro turnos de 6 horas para cobertura intensiva con rotación frecuente de personal.',
            'category': 'CUSTOM',
            'shift_type': 'ROTATING',
            'total_shifts_per_day': 4,
            'hours_per_shift': 6.0,
            'rotation_days': 5,
            'icon_name': 'fas fa-sync-alt',
            'color_primary': '#ea580c',
            'color_secondary': '#c2410c',
            'shifts_config': '[{"name":"DAWN","custom_name":"Madrugada","start_time":"00:00","end_time":"06:00","color":"#6366f1","icon":"fas fa-moon"},{"name":"MORNING","custom_name":"Mañana","start_time":"06:00","end_time":"12:00","color":"#f59e0b","icon":"fas fa-sun"},{"name":"AFTERNOON","custom_name":"Tarde","start_time":"12:00","end_time":"18:00","color":"#3b82f6","icon":"fas fa-cloud-sun"},{"name":"NIGHT","custom_name":"Noche","start_time":"18:00","end_time":"00:00","color":"#6366f1","icon":"fas fa-moon"}]',
            'is_default': False
        },
        {
            'name': 'Turno Partido (4+4 hrs)',
            'description': 'Turno dividido en dos bloques de 4 horas con descanso intermedio.',
            'category': 'CUSTOM',
            'shift_type': 'SPLIT',
            'total_shifts_per_day': 1,
            'hours_per_shift': 8.0,
            'rotation_days': 0,
            'icon_name': 'fas fa-cut',
            'color_primary': '#be185d',
            'color_secondary': '#9d174d',
            'shifts_config': '[{"name":"CUSTOM","custom_name":"Mañana","start_time":"08:00","end_time":"12:00","color":"#f59e0b","icon":"fas fa-sun"},{"name":"CUSTOM","custom_name":"Tarde","start_time":"16:00","end_time":"20:00","color":"#3b82f6","icon":"fas fa-cloud-sun"}]',
            'is_default': False
        }
    ]
    
    created_count = 0
    for template_data in templates_data:
        template, created = ShiftTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            print(f"✅ Creada: {template.name}")
            created_count += 1
        else:
            print(f"ℹ️  Ya existe: {template.name}")
    
    total_templates = ShiftTemplate.objects.count()
    
    print(f"\n🎊 ¡Proceso completado! {created_count} plantillas nuevas creadas.")
    print(f"📊 Total de plantillas disponibles: {total_templates}")
    print("\n🚀 ¡Sistema de turnos listo para usar!")
    print("💡 Los administradores ahora pueden configurar horarios desde la interfaz web")
    print("🌐 Accede a: /asistencia/turnos/")
    
    return True


if __name__ == "__main__":
    try:
        success = setup_shifts_in_production()
        if success:
            print("\n✅ CONFIGURACIÓN EXITOSA")
        else:
            print("\n❌ CONFIGURACIÓN FALLIDA")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
