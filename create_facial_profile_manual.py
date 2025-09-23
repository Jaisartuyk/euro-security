#!/usr/bin/env python3
"""
Script para crear perfiles faciales manualmente desde el admin
EURO SECURITY - Registro facial simplificado
"""
import os
import sys
import django
import json
import base64
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('.')
django.setup()

from employees.models import Employee
from attendance.models import FacialRecognitionProfile
from attendance.facial_recognition import facial_system

def create_facial_profile_manual():
    """Crear perfil facial manualmente"""
    print("🛡️ EURO SECURITY - Registro Facial Manual")
    print("=" * 50)
    
    # Listar empleados
    employees = Employee.objects.all()
    if not employees:
        print("❌ No hay empleados registrados")
        return
    
    print("👥 Empleados disponibles:")
    for i, emp in enumerate(employees, 1):
        print(f"{i}. {emp.first_name} {emp.last_name} ({emp.employee_id})")
    
    # Seleccionar empleado
    try:
        choice = int(input("\n🔢 Selecciona el número del empleado: ")) - 1
        employee = employees[choice]
        print(f"✅ Empleado seleccionado: {employee.first_name} {employee.last_name}")
    except (ValueError, IndexError):
        print("❌ Selección inválida")
        return
    
    # Verificar si ya tiene perfil
    try:
        existing_profile = employee.facial_profile
        print(f"⚠️ El empleado ya tiene un perfil facial")
        overwrite = input("¿Sobrescribir? (s/N): ").lower()
        if overwrite not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada")
            return
    except FacialRecognitionProfile.DoesNotExist:
        pass
    
    # Crear perfil con datos simulados (para prueba)
    print("\n🧬 Creando perfil facial...")
    
    # Simular características faciales para prueba
    simulated_features = {
        'histogram': [0.1] * 50,
        'lbp': [0.2] * 16,
        'edges': 0.15,
        'hu_moments': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        'color': [120, 130, 140],
        'gradient_mean': [0.25, 0.30]
    }
    
    # Crear o actualizar perfil
    profile, created = FacialRecognitionProfile.objects.get_or_create(
        employee=employee,
        defaults={
            'confidence_threshold': 0.75,
            'is_active': True,
            'needs_retraining': False
        }
    )
    
    # Codificar características
    features_json = json.dumps(simulated_features)
    profile.face_encoding = base64.b64encode(features_json.encode('utf-8')).decode('utf-8')
    profile.reference_images = "3"  # Simular 3 imágenes
    profile.save()
    
    action = "creado" if created else "actualizado"
    print(f"✅ Perfil facial {action} exitosamente")
    print(f"🎯 Umbral de confianza: {profile.confidence_threshold}")
    print(f"📊 Estado: {'Activo' if profile.is_active else 'Inactivo'}")
    
    print("\n🎉 ¡Listo! El empleado ya puede marcar asistencia con reconocimiento facial")
    print("🔗 Prueba en: http://127.0.0.1:8000/asistencia/marcar/")

def list_profiles():
    """Listar perfiles existentes"""
    print("\n📋 Perfiles faciales existentes:")
    profiles = FacialRecognitionProfile.objects.all()
    
    if not profiles:
        print("❌ No hay perfiles faciales registrados")
        return
    
    for profile in profiles:
        status = "✅ Activo" if profile.is_active else "❌ Inactivo"
        success_rate = 0
        if profile.total_recognitions > 0:
            success_rate = (profile.successful_recognitions / profile.total_recognitions) * 100
        
        print(f"👤 {profile.employee.first_name} {profile.employee.last_name}")
        print(f"   Estado: {status}")
        print(f"   Confianza: {profile.confidence_threshold}")
        print(f"   Reconocimientos: {profile.total_recognitions}")
        print(f"   Tasa de éxito: {success_rate:.1f}%")
        print()

def main():
    """Función principal"""
    while True:
        print("\n🛡️ EURO SECURITY - Gestión de Perfiles Faciales")
        print("1. Crear/Actualizar perfil facial")
        print("2. Listar perfiles existentes")
        print("3. Salir")
        
        choice = input("\nSelecciona una opción: ")
        
        if choice == '1':
            create_facial_profile_manual()
        elif choice == '2':
            list_profiles()
        elif choice == '3':
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()
