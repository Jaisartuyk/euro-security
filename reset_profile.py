#!/usr/bin/env python3
"""
Script para resetear perfil facial y probar sistema de primera vez
EURO SECURITY - Reset Profile
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models import FacialRecognitionProfile
from employees.models import Employee

def reset_profile():
    """Resetear perfil facial para probar primera vez"""
    print("🔄 EURO SECURITY - Reset de Perfil Facial")
    print("=" * 50)
    
    try:
        # Buscar perfil de JAIRO JAVIER SANCHEZ TRIANA
        employee = Employee.objects.get(first_name="JAIRO JAVIER", last_name="SANCHEZ TRIANA")
        print(f"👤 Empleado encontrado: {employee.first_name} {employee.last_name}")
        
        try:
            profile = employee.facial_profile
            print(f"📋 Perfil facial encontrado:")
            print(f"   Total reconocimientos: {profile.total_recognitions}")
            print(f"   Reconocimientos exitosos: {profile.successful_recognitions}")
            print(f"   Umbral: {profile.confidence_threshold}")
            
            # Confirmar eliminación
            confirm = input("\n¿Eliminar perfil facial para probar sistema de primera vez? (s/N): ")
            
            if confirm.lower() in ['s', 'si', 'sí', 'y', 'yes']:
                profile.delete()
                print("✅ Perfil facial eliminado exitosamente")
                print("\n🎯 PRÓXIMOS PASOS:")
                print("1. Ve a /asistencia/marcar/")
                print("2. El sistema detectará que es primera vez")
                print("3. Capturará automáticamente 5 fotos")
                print("4. Creará tu perfil facial automáticamente")
                print("5. Después funcionará normalmente")
            else:
                print("❌ Operación cancelada")
                
        except FacialRecognitionProfile.DoesNotExist:
            print("ℹ️ No hay perfil facial registrado")
            print("✅ Ya estás listo para probar el sistema de primera vez")
            
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")

if __name__ == "__main__":
    reset_profile()
