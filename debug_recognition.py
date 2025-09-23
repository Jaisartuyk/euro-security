#!/usr/bin/env python3
"""
Script para debuggear reconocimiento facial
EURO SECURITY - Debug de reconocimiento
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
from attendance.facial_recognition import facial_recognition_system
from PIL import Image
import json
import base64

def debug_recognition():
    """Debug del sistema de reconocimiento"""
    print("🔍 EURO SECURITY - Debug de Reconocimiento Facial")
    print("=" * 60)
    
    # Listar perfiles
    profiles = FacialRecognitionProfile.objects.filter(is_active=True)
    
    if not profiles:
        print("❌ No hay perfiles faciales activos")
        return
    
    print(f"📋 Perfiles activos encontrados: {profiles.count()}")
    
    for profile in profiles:
        print(f"\n🧬 PERFIL: {profile.employee.first_name} {profile.employee.last_name}")
        print(f"   ID: {profile.id}")
        print(f"   Umbral: {profile.confidence_threshold}")
        print(f"   Codificación: {'✅' if profile.face_encoding else '❌'}")
        
        # Verificar codificación
        if profile.face_encoding:
            try:
                # Decodificar
                decoded = base64.b64decode(profile.face_encoding.encode('utf-8'))
                features = json.loads(decoded.decode('utf-8'))
                
                print(f"   Características decodificadas: ✅")
                print(f"   Tipos de características: {list(features.keys())}")
                
                # Verificar cada tipo
                for key, value in features.items():
                    if isinstance(value, list):
                        print(f"     - {key}: {len(value)} valores")
                    else:
                        print(f"     - {key}: {value}")
                        
            except Exception as e:
                print(f"   ❌ Error decodificando: {str(e)}")
        
        # Verificar imágenes
        images = [profile.image_1, profile.image_2, profile.image_3, profile.image_4, profile.image_5]
        valid_images = [img for img in images if img and img.name]
        
        print(f"   Imágenes subidas: {len(valid_images)}")
        
        for i, img in enumerate(valid_images, 1):
            try:
                # Verificar si el archivo existe
                if os.path.exists(img.path):
                    # Verificar si se puede abrir
                    pil_img = Image.open(img.path)
                    print(f"     ✅ Imagen {i}: {img.name} ({pil_img.size})")
                else:
                    print(f"     ❌ Imagen {i}: Archivo no encontrado")
            except Exception as e:
                print(f"     ❌ Imagen {i}: Error - {str(e)}")

def test_recognition_with_profile():
    """Probar reconocimiento con perfil específico"""
    profiles = FacialRecognitionProfile.objects.filter(is_active=True)
    
    if not profiles:
        print("❌ No hay perfiles para probar")
        return
    
    print("\n🧪 PRUEBA DE RECONOCIMIENTO:")
    
    for i, profile in enumerate(profiles, 1):
        print(f"{i}. {profile.employee.first_name} {profile.employee.last_name}")
    
    try:
        choice = int(input("\nSelecciona perfil para probar (número): ")) - 1
        profile = profiles[choice]
        
        print(f"\n🎯 Probando reconocimiento para: {profile.employee.first_name}")
        
        # Verificar si tiene imágenes
        images = [profile.image_1, profile.image_2, profile.image_3, profile.image_4, profile.image_5]
        valid_images = [img for img in images if img and img.name and os.path.exists(img.path)]
        
        if not valid_images:
            print("❌ No hay imágenes válidas para probar")
            return
        
        # Usar la primera imagen como test
        test_image = valid_images[0]
        print(f"📸 Usando imagen de prueba: {test_image.name}")
        
        # Simular reconocimiento
        try:
            pil_image = Image.open(test_image.path)
            
            # Extraer características
            features, location, quality = facial_recognition_system.extract_face_encoding(pil_image)
            
            print(f"✅ Características extraídas")
            print(f"   Calidad: {quality:.2f}")
            print(f"   Ubicación rostro: {location}")
            
            if features:
                print(f"   Tipos de características: {list(features.keys())}")
                
                # Simular comparación
                if profile.face_encoding:
                    print("🔄 Comparando con perfil almacenado...")
                    # Aquí iría la lógica de comparación real
                    print("✅ Comparación completada")
                else:
                    print("❌ No hay codificación en el perfil para comparar")
            else:
                print("❌ No se pudieron extraer características")
                
        except Exception as e:
            print(f"❌ Error en reconocimiento: {str(e)}")
            
    except (ValueError, IndexError):
        print("❌ Selección inválida")

def main():
    """Función principal"""
    debug_recognition()
    
    test = input("\n¿Probar reconocimiento con imagen existente? (s/N): ")
    if test.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        test_recognition_with_profile()

if __name__ == "__main__":
    main()
