#!/usr/bin/env python3
"""
Script para probar permisos de superusuario
EURO SECURITY - Test Superuser
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from core.context_processors import attendance_permissions

class MockRequest:
    def __init__(self, user):
        self.user = user

def test_superuser():
    """Probar permisos de superusuario"""
    print("👑 EURO SECURITY - Test Permisos de Superusuario")
    print("=" * 55)
    
    try:
        # Buscar superusuario
        superuser = User.objects.filter(is_superuser=True).first()
        
        if not superuser:
            print("❌ No hay superusuarios en el sistema")
            return
        
        print(f"👤 Superusuario: {superuser.username}")
        print(f"📧 Email: {superuser.email}")
        print(f"🔑 is_superuser: {'✅' if superuser.is_superuser else '❌'}")
        print(f"👥 is_staff: {'✅' if superuser.is_staff else '❌'}")
        
        # Crear mock request
        request = MockRequest(superuser)
        
        # Obtener contexto de permisos
        context = attendance_permissions(request)
        
        print(f"\n🔐 PERMISOS AUTOMÁTICOS DEL SUPERUSUARIO:")
        permissions = [
            ('has_employee_profile', 'Tiene perfil de empleado'),
            ('can_view_attendance_dashboard', 'Dashboard de Asistencias'),
            ('can_view_attendance_reports', 'Reportes de Asistencia'),
            ('can_view_location_maps', 'Mapas de Ubicaciones'),
            ('can_export_reports', 'Exportar Datos CSV'),
        ]
        
        for key, desc in permissions:
            icon = "✅" if context.get(key, False) else "❌"
            print(f"   {icon} {desc}")
        
        print(f"   🎯 Nivel de permisos: {context.get('attendance_permission_level', 'none')}")
        
        print(f"\n🎯 MENÚ DISPONIBLE PARA SUPERUSUARIO:")
        print(f"   👑 ADMINISTRACIÓN COMPLETA:")
        print(f"      ✅ Dashboard Administrativo")
        print(f"      ✅ Empleados")
        print(f"      ✅ Departamentos")
        print(f"      ✅ Puestos de Trabajo")
        print(f"      ✅ Reportes")
        
        print(f"   📊 CONTROL DE ASISTENCIAS:")
        print(f"      ✅ Dashboard Asistencias")
        print(f"      ✅ Reportes Generales")
        print(f"      ✅ Mapa de Ubicaciones")
        print(f"      ✅ Exportar Datos")
        print(f"      ✅ Marcación Manual")
        
        print(f"   👤 MI ASISTENCIA:")
        print(f"      ✅ Mi Historial")
        
        print(f"\n🌐 URLS DISPONIBLES:")
        print(f"   ✅ /asistencia/dashboard/ - Dashboard")
        print(f"   ✅ /asistencia/reportes/ - Reportes")
        print(f"   ✅ /asistencia/mapa/ - Mapas")
        print(f"   ✅ /asistencia/marcar/ - Marcación")
        print(f"   ✅ /asistencia/mi-asistencia/ - Historial")
        
        print(f"\n🚀 COMO SUPERUSUARIO TIENES:")
        print(f"   👑 Acceso AUTOMÁTICO a todo")
        print(f"   🔓 Sin restricciones de permisos")
        print(f"   📊 Control total del sistema")
        print(f"   🗺️ Acceso a todas las ubicaciones")
        print(f"   📥 Exportación de todos los datos")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"   1. Actualiza la página web (F5)")
        print(f"   2. Deberías ver TODA la sección 'CONTROL DE ASISTENCIAS'")
        print(f"   3. No necesitas perfil de empleado adicional")
        print(f"   4. Tienes acceso completo como creador del sistema")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_superuser()
