#!/usr/bin/env python3
"""
Diagnóstico profundo del sistema de reconocimiento facial
EURO SECURITY - Deep Debug
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models import FacialRecognitionProfile, AttendanceRecord
from attendance.facial_recognition import facial_recognition_system
from employees.models import Employee
from django.contrib.auth.models import User
from PIL import Image
import json
import base64

def check_user_session():
    """Verificar qué usuario está siendo usado"""
    print("👤 VERIFICACIÓN DE USUARIO:")
    print("-" * 40)
    
    # Verificar usuario jairo javier.sanchez
    try:
        user = User.objects.get(username='jairo javier.sanchez')
        print(f"✅ Usuario encontrado: {user.username}")
        print(f"   Activo: {'✅' if user.is_active else '❌'}")
        print(f"   Staff: {'✅' if user.is_staff else '❌'}")
        
        # Verificar empleado asociado
        try:
            employee = Employee.objects.get(user=user)
            print(f"✅ Empleado asociado: {employee.first_name} {employee.last_name}")
            print(f"   ID: {employee.employee_id}")
            print(f"   Departamento: {employee.department.name}")
            
            # Verificar perfil facial
            try:
                profile = employee.facial_profile
                print(f"✅ Perfil facial: Existe")
                print(f"   Activo: {'✅' if profile.is_active else '❌'}")
                print(f"   Umbral: {profile.confidence_threshold}")
                return user, employee, profile
            except FacialRecognitionProfile.DoesNotExist:
                print("❌ No tiene perfil facial")
                return user, employee, None
                
        except Employee.DoesNotExist:
            print("❌ Usuario no tiene empleado asociado")
            return user, None, None
            
    except User.DoesNotExist:
        print("❌ Usuario 'jairo javier.sanchez' no encontrado")
        return None, None, None

def test_facial_recognition_step_by_step(profile):
    """Probar reconocimiento paso a paso"""
    print("\n🧪 PRUEBA PASO A PASO:")
    print("-" * 40)
    
    if not profile:
        print("❌ No hay perfil para probar")
        return
    
    # Verificar imágenes
    images = [profile.image_1, profile.image_2, profile.image_3, profile.image_4, profile.image_5]
    valid_images = [img for img in images if img and img.name and os.path.exists(img.path)]
    
    if not valid_images:
        print("❌ No hay imágenes válidas")
        return
    
    print(f"📸 Imágenes disponibles: {len(valid_images)}")
    
    # Usar primera imagen como test
    test_image = valid_images[0]
    print(f"🔍 Probando con: {test_image.name}")
    
    try:
        # Paso 1: Abrir imagen
        pil_image = Image.open(test_image.path)
        print(f"✅ Imagen abierta: {pil_image.size}")
        
        # Paso 2: Extraer características
        print("🔄 Extrayendo características...")
        features, location, quality = facial_recognition_system.extract_face_encoding(pil_image)
        
        if features:
            print(f"✅ Características extraídas")
            print(f"   Calidad: {quality:.3f}")
            print(f"   Ubicación rostro: {location}")
            print(f"   Tipos: {list(features.keys())}")
            
            # Paso 3: Comparar con perfil almacenado
            if profile.face_encoding:
                print("🔄 Comparando con perfil almacenado...")
                
                try:
                    # Decodificar perfil almacenado
                    decoded = base64.b64decode(profile.face_encoding.encode('utf-8'))
                    stored_features = json.loads(decoded.decode('utf-8'))
                    
                    print("✅ Perfil almacenado decodificado")
                    
                    # Simular comparación manual
                    similarity = calculate_manual_similarity(features, stored_features)
                    print(f"📊 Similitud calculada: {similarity:.3f}")
                    print(f"📊 Umbral requerido: {profile.confidence_threshold}")
                    
                    if similarity >= profile.confidence_threshold:
                        print("✅ RECONOCIMIENTO EXITOSO")
                    else:
                        print("❌ RECONOCIMIENTO FALLIDO")
                        print(f"   Diferencia: {profile.confidence_threshold - similarity:.3f}")
                        
                        # Sugerir nuevo umbral
                        suggested = max(0.50, similarity - 0.05)
                        print(f"💡 Umbral sugerido: {suggested:.2f}")
                    
                except Exception as e:
                    print(f"❌ Error comparando: {str(e)}")
            else:
                print("❌ No hay perfil almacenado para comparar")
        else:
            print("❌ No se pudieron extraer características")
            print(f"   Calidad: {quality:.3f}")
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")

def calculate_manual_similarity(features1, features2):
    """Calcular similitud manual entre características"""
    import numpy as np
    
    similarities = []
    
    # Comparar histogramas
    if 'histogram' in features1 and 'histogram' in features2:
        hist1 = np.array(features1['histogram'])
        hist2 = np.array(features2['histogram'])
        if len(hist1) == len(hist2):
            # Correlación de histogramas
            correlation = np.corrcoef(hist1, hist2)[0, 1]
            if not np.isnan(correlation):
                similarities.append(abs(correlation))
    
    # Comparar LBP
    if 'lbp' in features1 and 'lbp' in features2:
        lbp1 = np.array(features1['lbp'])
        lbp2 = np.array(features2['lbp'])
        if len(lbp1) == len(lbp2):
            # Distancia euclidiana normalizada
            distance = np.linalg.norm(lbp1 - lbp2)
            max_distance = np.linalg.norm(lbp1) + np.linalg.norm(lbp2)
            if max_distance > 0:
                similarity = 1 - (distance / max_distance)
                similarities.append(max(0, similarity))
    
    # Comparar momentos de Hu
    if 'hu_moments' in features1 and 'hu_moments' in features2:
        hu1 = np.array(features1['hu_moments'])
        hu2 = np.array(features2['hu_moments'])
        if len(hu1) == len(hu2):
            # Distancia de momentos de Hu
            distance = np.sum(np.abs(hu1 - hu2))
            similarity = 1 / (1 + distance)
            similarities.append(similarity)
    
    # Promedio de similitudes
    if similarities:
        return np.mean(similarities)
    else:
        return 0.0

def check_recent_attempts(employee):
    """Verificar intentos recientes"""
    print("\n📊 INTENTOS RECIENTES:")
    print("-" * 40)
    
    # Buscar registros recientes
    recent_records = AttendanceRecord.objects.filter(
        employee=employee
    ).order_by('-timestamp')[:10]
    
    if recent_records:
        print(f"📋 Últimos {len(recent_records)} registros:")
        for record in recent_records:
            status = "✅ Válido" if record.is_valid else "❌ Inválido"
            print(f"   {record.timestamp.strftime('%H:%M:%S')} - {record.attendance_type} - {status}")
    else:
        print("📋 No hay registros de asistencia")

def suggest_solutions(profile):
    """Sugerir soluciones específicas"""
    print("\n💡 SOLUCIONES SUGERIDAS:")
    print("-" * 40)
    
    if not profile:
        print("1. Crear perfil facial desde admin")
        return
    
    success_rate = 0
    if profile.total_recognitions > 0:
        success_rate = (profile.successful_recognitions / profile.total_recognitions) * 100
    
    print(f"📊 Tasa actual: {success_rate:.1f}%")
    print(f"📊 Umbral actual: {profile.confidence_threshold}")
    
    if success_rate == 0 and profile.total_recognitions > 5:
        print("\n🚨 PROBLEMA CRÍTICO: 0% de éxito")
        print("SOLUCIONES:")
        print("1. Bajar umbral a 0.55")
        print("2. Recrear perfil con mejores imágenes")
        print("3. Verificar iluminación de la cámara")
        
    elif success_rate < 30:
        print("\n⚠️ PROBLEMA: Baja tasa de éxito")
        print("SOLUCIONES:")
        print("1. Bajar umbral en 0.10")
        print("2. Agregar más imágenes de referencia")
        
    else:
        print("\n✅ Perfil parece estar bien configurado")
        print("VERIFICAR:")
        print("1. ¿Estás usando el usuario correcto?")
        print("2. ¿La cámara tiene buena iluminación?")
        print("3. ¿El rostro está bien centrado?")

def main():
    """Función principal"""
    print("🔍 EURO SECURITY - Diagnóstico Profundo")
    print("=" * 60)
    
    # Verificar usuario y empleado
    user, employee, profile = check_user_session()
    
    if not user or not employee:
        print("\n❌ PROBLEMA FUNDAMENTAL: Usuario o empleado no encontrado")
        return
    
    # Probar reconocimiento paso a paso
    test_facial_recognition_step_by_step(profile)
    
    # Verificar intentos recientes
    check_recent_attempts(employee)
    
    # Sugerir soluciones
    suggest_solutions(profile)
    
    print("\n" + "=" * 60)
    print("🎯 PRÓXIMOS PASOS RECOMENDADOS:")
    
    if profile and profile.total_recognitions > 0:
        success_rate = (profile.successful_recognitions / profile.total_recognitions) * 100
        if success_rate == 0:
            print("1. Ejecutar: python fix_recognition.py")
            print("2. Bajar umbral manualmente a 0.55")
            print("3. Probar con mejor iluminación")
    else:
        print("1. Verificar que estás logueado como 'jairo javier.sanchez'")
        print("2. Ir a /asistencia/marcar/ y probar")
        print("3. Verificar que la cámara funciona")

if __name__ == "__main__":
    main()
