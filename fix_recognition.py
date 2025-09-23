#!/usr/bin/env python3
"""
Script para arreglar problemas de reconocimiento facial
EURO SECURITY - Fix de reconocimiento
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models import FacialRecognitionProfile

def fix_recognition_issues():
    """Arreglar problemas comunes de reconocimiento"""
    print("🔧 EURO SECURITY - Arreglo de Reconocimiento Facial")
    print("=" * 60)
    
    profiles = FacialRecognitionProfile.objects.all()
    
    if not profiles:
        print("❌ No hay perfiles faciales")
        return
    
    for profile in profiles:
        print(f"\n📋 PERFIL: {profile.employee.first_name} {profile.employee.last_name}")
        print(f"   Total intentos: {profile.total_recognitions}")
        print(f"   Exitosos: {profile.successful_recognitions}")
        
        if profile.total_recognitions > 0:
            success_rate = (profile.successful_recognitions / profile.total_recognitions) * 100
            print(f"   Tasa actual: {success_rate:.1f}%")
            
            # Si la tasa de éxito es muy baja, ajustar umbral
            if success_rate < 50 and profile.total_recognitions > 5:
                old_threshold = profile.confidence_threshold
                new_threshold = max(0.50, old_threshold - 0.15)  # Bajar 15% pero mínimo 50%
                
                profile.confidence_threshold = new_threshold
                profile.needs_retraining = False  # Quitar flag de reentrenamiento
                profile.save()
                
                print(f"   🔧 AJUSTADO: Umbral {old_threshold} → {new_threshold}")
                print(f"   ✅ Perfil actualizado")
            
            elif success_rate == 0 and profile.total_recognitions > 10:
                # Caso extremo: muchos intentos, 0% éxito
                old_threshold = profile.confidence_threshold
                new_threshold = 0.55  # Umbral muy bajo para casos difíciles
                
                profile.confidence_threshold = new_threshold
                profile.needs_retraining = False
                profile.save()
                
                print(f"   🚨 CASO EXTREMO: Umbral {old_threshold} → {new_threshold}")
                print(f"   ✅ Perfil actualizado para caso difícil")
        
        else:
            print(f"   ℹ️ Sin intentos de reconocimiento aún")

def reset_statistics():
    """Reiniciar estadísticas para empezar de cero"""
    print("\n🔄 ¿REINICIAR ESTADÍSTICAS?")
    
    profiles = FacialRecognitionProfile.objects.all()
    
    for profile in profiles:
        if profile.total_recognitions > 0:
            print(f"   {profile.employee.first_name}: {profile.total_recognitions} intentos")
    
    reset = input("\n¿Reiniciar estadísticas de todos los perfiles? (s/N): ")
    
    if reset.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        for profile in profiles:
            profile.total_recognitions = 0
            profile.successful_recognitions = 0
            profile.last_recognition = None
            profile.save()
        
        print("✅ Estadísticas reiniciadas para todos los perfiles")
        print("💡 Ahora puedes probar el reconocimiento desde cero")

def optimize_specific_profile():
    """Optimizar perfil específico"""
    print("\n🎯 OPTIMIZACIÓN ESPECÍFICA:")
    
    profiles = FacialRecognitionProfile.objects.all()
    
    for i, profile in enumerate(profiles, 1):
        success_rate = 0
        if profile.total_recognitions > 0:
            success_rate = (profile.successful_recognitions / profile.total_recognitions) * 100
        
        print(f"{i}. {profile.employee.first_name} {profile.employee.last_name}")
        print(f"   Umbral actual: {profile.confidence_threshold}")
        print(f"   Tasa de éxito: {success_rate:.1f}%")
    
    try:
        choice = int(input("\nSelecciona perfil para optimizar (número): ")) - 1
        profile = profiles[choice]
        
        print(f"\n🔧 OPTIMIZANDO: {profile.employee.first_name} {profile.employee.last_name}")
        
        # Sugerir nuevo umbral basado en estadísticas
        if profile.total_recognitions > 0:
            success_rate = (profile.successful_recognitions / profile.total_recognitions) * 100
            
            if success_rate == 0:
                suggested_threshold = 0.55
                print(f"💡 SUGERENCIA: Umbral muy bajo (0.55) - 0% éxito actual")
            elif success_rate < 30:
                suggested_threshold = max(0.60, profile.confidence_threshold - 0.10)
                print(f"💡 SUGERENCIA: Reducir umbral a {suggested_threshold}")
            elif success_rate > 90:
                suggested_threshold = min(0.85, profile.confidence_threshold + 0.05)
                print(f"💡 SUGERENCIA: Aumentar umbral a {suggested_threshold} (muy buena tasa)")
            else:
                suggested_threshold = profile.confidence_threshold
                print(f"💡 SUGERENCIA: Mantener umbral actual ({suggested_threshold})")
        else:
            suggested_threshold = 0.65
            print(f"💡 SUGERENCIA: Umbral inicial recomendado (0.65)")
        
        new_threshold = input(f"Nuevo umbral (actual: {profile.confidence_threshold}, sugerido: {suggested_threshold}): ")
        
        if new_threshold:
            try:
                threshold_value = float(new_threshold)
                if 0.3 <= threshold_value <= 0.95:
                    profile.confidence_threshold = threshold_value
                    profile.needs_retraining = False
                    profile.save()
                    print(f"✅ Umbral actualizado a {threshold_value}")
                else:
                    print("❌ Umbral debe estar entre 0.3 y 0.95")
            except ValueError:
                print("❌ Valor inválido")
        
    except (ValueError, IndexError):
        print("❌ Selección inválida")

def main():
    """Función principal"""
    fix_recognition_issues()
    
    print("\n" + "="*60)
    print("🛠️ OPCIONES ADICIONALES:")
    print("1. Reiniciar estadísticas")
    print("2. Optimizar perfil específico")
    print("3. Salir")
    
    choice = input("\nSelecciona opción (1-3): ")
    
    if choice == '1':
        reset_statistics()
    elif choice == '2':
        optimize_specific_profile()
    elif choice == '3':
        print("👋 ¡Listo!")
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
