#!/usr/bin/env python3
"""
Script para verificar perfiles faciales existentes
EURO SECURITY - Diagnóstico de reconocimiento facial
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from employees.models import Employee
from attendance.models import FacialRecognitionProfile
from django.contrib.auth.models import User

def check_facial_profiles():
    """Verificar todos los perfiles faciales"""
    print("🛡️ EURO SECURITY - Diagnóstico de Perfiles Faciales")
    print("=" * 60)
    
    # Verificar usuarios
    print("\n👥 USUARIOS REGISTRADOS:")
    users = User.objects.all()
    for user in users:
        print(f"   - {user.username} ({'Activo' if user.is_active else 'Inactivo'})")
    
    # Verificar empleados
    print("\n👨‍💼 EMPLEADOS REGISTRADOS:")
    employees = Employee.objects.all()
    if not employees:
        print("   ❌ No hay empleados registrados")
        return
    
    for emp in employees:
        print(f"   - {emp.first_name} {emp.last_name} ({emp.employee_id})")
        print(f"     Usuario: {emp.user.username if emp.user else 'Sin usuario'}")
        print(f"     Departamento: {emp.department.name}")
        print(f"     Puesto: {emp.position.title}")
    
    # Verificar perfiles faciales
    print("\n🧬 PERFILES FACIALES:")
    profiles = FacialRecognitionProfile.objects.all()
    
    if not profiles:
        print("   ❌ NO HAY PERFILES FACIALES REGISTRADOS")
        print("\n🔧 SOLUCIÓN:")
        print("   1. Ve a /admin/attendance/facialrecognitionprofile/add/")
        print("   2. Crea un perfil para tu empleado")
        print("   3. Sube 2-3 imágenes de referencia")
        return
    
    for profile in profiles:
        print(f"\n📋 PERFIL: {profile.employee.first_name} {profile.employee.last_name}")
        print(f"   Estado: {'✅ Activo' if profile.is_active else '❌ Inactivo'}")
        print(f"   Umbral de confianza: {profile.confidence_threshold}")
        print(f"   Codificación facial: {'✅ Sí' if profile.face_encoding else '❌ No'}")
        print(f"   Imágenes de referencia: {profile.reference_images or '0'}")
        print(f"   Total reconocimientos: {profile.total_recognitions}")
        print(f"   Reconocimientos exitosos: {profile.successful_recognitions}")
        
        # Verificar imágenes subidas
        images = [profile.image_1, profile.image_2, profile.image_3, profile.image_4, profile.image_5]
        valid_images = [img for img in images if img and img.name]
        print(f"   Imágenes subidas: {len(valid_images)}")
        
        for i, img in enumerate(valid_images, 1):
            print(f"     - Imagen {i}: {img.name}")
        
        if profile.needs_retraining:
            print("   ⚠️ NECESITA REENTRENAMIENTO")
        
        # Verificar si tiene codificación
        if not profile.face_encoding:
            print("   🔧 PROBLEMA: Sin codificación facial")
            print("   💡 SOLUCIÓN: Reprocesar imágenes")

def create_test_profile():
    """Crear perfil de prueba"""
    print("\n🔧 ¿CREAR PERFIL DE PRUEBA?")
    
    employees = Employee.objects.all()
    if not employees:
        print("❌ No hay empleados para crear perfil")
        return
    
    print("Empleados disponibles:")
    for i, emp in enumerate(employees, 1):
        print(f"{i}. {emp.first_name} {emp.last_name}")
    
    try:
        choice = input("\nSelecciona empleado (número) o 'n' para cancelar: ")
        if choice.lower() == 'n':
            return
        
        employee = employees[int(choice) - 1]
        
        # Verificar si ya tiene perfil
        try:
            existing = employee.facial_profile
            print(f"⚠️ {employee.first_name} ya tiene perfil facial")
            return
        except FacialRecognitionProfile.DoesNotExist:
            pass
        
        # Crear perfil básico
        profile = FacialRecognitionProfile.objects.create(
            employee=employee,
            confidence_threshold=0.75,
            is_active=True,
            needs_retraining=False,
            face_encoding="",  # Vacío por ahora
            reference_images="0"
        )
        
        print(f"✅ Perfil creado para {employee.first_name} {employee.last_name}")
        print("📝 PRÓXIMOS PASOS:")
        print("1. Ve al admin: /admin/attendance/facialrecognitionprofile/")
        print("2. Edita el perfil creado")
        print("3. Sube 2-3 imágenes de referencia")
        print("4. Guarda → Sistema procesará automáticamente")
        
    except (ValueError, IndexError):
        print("❌ Selección inválida")

def main():
    """Función principal"""
    check_facial_profiles()
    
    profiles = FacialRecognitionProfile.objects.all()
    if not profiles:
        create_test_profile()

if __name__ == "__main__":
    main()
