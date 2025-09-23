#!/usr/bin/env python3
"""
Script para probar el nuevo menú de navegación
EURO SECURITY - Test Menu
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from core.context_processors import attendance_permissions
from employees.models import Employee
from django.contrib.auth.models import User

class MockRequest:
    def __init__(self, user):
        self.user = user

def test_menu_permissions():
    """Probar permisos del menú de navegación"""
    print("🎯 EURO SECURITY - Test Menú de Navegación")
    print("=" * 50)
    
    try:
        # Buscar empleado de prueba
        employee = Employee.objects.get(first_name="JAIRO JAVIER", last_name="SANCHEZ TRIANA")
        user = employee.user
        
        print(f"👤 Usuario de prueba: {employee.get_full_name()}")
        print(f"🏢 Departamento: {employee.department.name if employee.department else 'Sin departamento'}")
        print(f"💼 Puesto: {employee.position.title}")
        print(f"🎯 Nivel: {employee.position.get_level_display()}")
        
        # Crear mock request
        request = MockRequest(user)
        
        # Obtener contexto de permisos
        context = attendance_permissions(request)
        
        print(f"\n🔐 PERMISOS EN EL CONTEXTO:")
        for key, value in context.items():
            icon = "✅" if value else "❌"
            print(f"   {icon} {key}: {value}")
        
        print(f"\n🎯 MENÚ VISIBLE PARA ESTE USUARIO:")
        
        # Simular lógica del menú
        if context['can_view_attendance_dashboard']:
            print(f"   📊 CONTROL DE ASISTENCIAS:")
            print(f"      ✅ Dashboard Asistencias")
            
            if context['can_view_attendance_reports']:
                level = context['attendance_permission_level']
                if level == 'full':
                    print(f"      ✅ Reportes Generales")
                elif level == 'management':
                    print(f"      ✅ Reportes Departamentales")
                else:
                    print(f"      ✅ Reportes de Mi Equipo")
            
            if context['can_view_location_maps']:
                print(f"      ✅ Mapa de Ubicaciones")
            
            if context['can_export_reports']:
                print(f"      ✅ Exportar Datos")
            
            level = context['attendance_permission_level']
            if level in ['full', 'management']:
                print(f"      ✅ Marcación Manual")
            else:
                print(f"      ✅ Marcar Asistencia")
        
        if context['has_employee_profile']:
            print(f"   👤 MI ASISTENCIA:")
            if not context['can_view_attendance_dashboard']:
                print(f"      ✅ Marcar Asistencia")
            print(f"      ✅ Mi Historial")
        
        print(f"\n🌐 URLS DISPONIBLES:")
        if context['can_view_attendance_dashboard']:
            print(f"   ✅ /asistencia/dashboard/ - Dashboard")
        if context['can_view_attendance_reports']:
            print(f"   ✅ /asistencia/reportes/ - Reportes")
        if context['can_view_location_maps']:
            print(f"   ✅ /asistencia/mapa/ - Mapas")
        print(f"   ✅ /asistencia/marcar/ - Marcación")
        print(f"   ✅ /asistencia/mi-asistencia/ - Historial personal")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"   1. Reinicia el servidor si está corriendo")
        print(f"   2. Ve a cualquier página del sistema")
        print(f"   3. Verifica que el menú lateral muestre las opciones correctas")
        print(f"   4. Prueba los enlaces de Control de Asistencias")
        
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_menu_permissions()
