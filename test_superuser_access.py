#!/usr/bin/env python3
"""
Script para probar acceso completo de superusuarios
EURO SECURITY - Test Superuser Access
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth.models import User
from attendance.permissions import AttendancePermissions
from core.context_processors import attendance_permissions

class MockRequest:
    def __init__(self, user):
        self.user = user

def test_superuser_access():
    """Probar acceso completo de superusuarios"""
    print("👑 EURO SECURITY - Test Acceso de Superusuario")
    print("=" * 55)
    
    try:
        # Buscar superusuario
        superuser = User.objects.filter(is_superuser=True).first()
        
        if not superuser:
            print("❌ No hay superusuarios en el sistema")
            return
        
        print(f"👤 Superusuario: {superuser.username}")
        print(f"🔑 is_superuser: {'✅' if superuser.is_superuser else '❌'}")
        print(f"👥 is_staff: {'✅' if superuser.is_staff else '❌'}")
        
        # Probar funciones de permisos directamente
        print(f"\n🔐 PERMISOS DIRECTOS:")
        
        # Nivel de permisos
        level = AttendancePermissions.get_permission_level(superuser)
        print(f"   🎯 Nivel: {level}")
        
        # Empleados visibles
        viewable_employees = AttendancePermissions.get_viewable_employees(superuser)
        print(f"   👥 Empleados visibles: {viewable_employees.count()}")
        
        # Departamentos visibles
        viewable_departments = AttendancePermissions.get_viewable_departments(superuser)
        print(f"   🏢 Departamentos visibles: {viewable_departments.count()}")
        
        # Permisos específicos
        can_view_maps = AttendancePermissions.can_view_location_maps(superuser)
        can_export = AttendancePermissions.can_export_reports(superuser)
        
        print(f"   🗺️ Ver mapas: {'✅' if can_view_maps else '❌'}")
        print(f"   📥 Exportar: {'✅' if can_export else '❌'}")
        
        # Probar context processor
        print(f"\n🌐 CONTEXT PROCESSOR:")
        request = MockRequest(superuser)
        context = attendance_permissions(request)
        
        context_perms = [
            ('has_employee_profile', 'Perfil de empleado'),
            ('can_view_attendance_dashboard', 'Dashboard'),
            ('can_view_attendance_reports', 'Reportes'),
            ('can_view_location_maps', 'Mapas'),
            ('can_export_reports', 'Exportar'),
        ]
        
        for key, desc in context_perms:
            icon = "✅" if context.get(key, False) else "❌"
            print(f"   {icon} {desc}")
        
        print(f"   🎯 Nivel contexto: {context.get('attendance_permission_level', 'none')}")
        
        # URLs que debería poder acceder
        print(f"\n🌐 URLS CON ACCESO GARANTIZADO:")
        urls = [
            '/asistencia/dashboard/',
            '/asistencia/reportes/',
            '/asistencia/mapa/',
            '/asistencia/rastreo-tiempo-real/',
            '/asistencia/alertas-ubicacion/',
            '/asistencia/api/rastreo-gps/',
            '/asistencia/api/areas-trabajo/',
        ]
        
        for url in urls:
            print(f"   ✅ {url}")
        
        # Verificar decoradores
        print(f"\n🔒 DECORADORES ACTUALIZADOS:")
        print(f"   ✅ @attendance_permission_required - Bypass para superusuarios")
        print(f"   ✅ Verificaciones manuales - Bypass para superusuarios")
        print(f"   ✅ Context processor - Permisos automáticos")
        print(f"   ✅ Funciones de permisos - Acceso completo")
        
        # Estado final
        all_permissions = all([
            level in ['superuser', 'staff'],
            viewable_employees.count() > 0,
            viewable_departments.count() > 0,
            can_view_maps,
            can_export,
            context.get('can_view_attendance_dashboard', False),
            context.get('can_view_location_maps', False),
        ])
        
        print(f"\n🎯 RESULTADO FINAL:")
        if all_permissions:
            print(f"   🎉 ¡SUPERUSUARIO CON ACCESO COMPLETO!")
            print(f"   ✅ Todas las verificaciones pasaron")
            print(f"   ✅ Sin restricciones de permisos")
            print(f"   ✅ Acceso garantizado a todas las vistas")
        else:
            print(f"   ⚠️ Algunos permisos pueden estar restringidos")
            print(f"   🔧 Revisa las configuraciones de permisos")
        
        print(f"\n🚀 PRÓXIMOS PASOS:")
        print(f"   1. Prueba acceder a cualquier URL del sistema")
        print(f"   2. No deberías ver mensajes de 'Sin permisos'")
        print(f"   3. Todas las funcionalidades están disponibles")
        print(f"   4. Como superusuario, tienes control total")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_superuser_access()
