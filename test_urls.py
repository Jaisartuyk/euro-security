#!/usr/bin/env python3
"""
Script para probar las URLs del sistema
EURO SECURITY - Test URLs
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from employees.models import Employee

def test_urls():
    """Probar URLs del sistema"""
    print("🌐 EURO SECURITY - Test URLs")
    print("=" * 40)
    
    try:
        # Probar URLs de attendance
        urls_to_test = [
            ('attendance:clock', 'Marcación'),
            ('attendance:dashboard', 'Dashboard'),
            ('attendance:reports', 'Reportes'),
            ('attendance:locations_map', 'Mapa'),
            ('attendance:my_attendance', 'Mi Asistencia'),
        ]
        
        print("🔗 PROBANDO URLs:")
        for url_name, description in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"   ✅ {description}: {url}")
            except Exception as e:
                print(f"   ❌ {description}: Error - {str(e)}")
        
        # Probar URLs con parámetros
        print(f"\n🔗 URLs CON PARÁMETROS:")
        try:
            url = reverse('attendance:department_report', kwargs={'department_id': 1})
            print(f"   ✅ Reporte Departamental: {url}")
        except Exception as e:
            print(f"   ❌ Reporte Departamental: Error - {str(e)}")
        
        # Probar APIs
        print(f"\n🔗 APIs:")
        api_urls = [
            ('attendance:locations_api', 'API Ubicaciones'),
            ('attendance:export_report', 'Exportar Reporte'),
            ('attendance:emergency_record', 'Modo Emergencia'),
        ]
        
        for url_name, description in api_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {description}: {url}")
            except Exception as e:
                print(f"   ❌ {description}: Error - {str(e)}")
        
        print(f"\n🎯 RESULTADO:")
        print(f"   El sistema debería funcionar correctamente")
        print(f"   Ve a: http://127.0.0.1:8000/asistencia/reportes/")
        
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_urls()
