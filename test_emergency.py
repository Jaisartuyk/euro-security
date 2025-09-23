#!/usr/bin/env python3
"""
Script para probar el modo de emergencia del reconocimiento facial
EURO SECURITY - Test Emergency Mode
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from attendance.models import AttendanceRecord, FacialRecognitionProfile
from employees.models import Employee
from django.utils import timezone

def test_emergency_mode():
    """Probar el modo de emergencia"""
    print("🚨 EURO SECURITY - Test Modo de Emergencia")
    print("=" * 50)
    
    try:
        # Buscar empleado
        employee = Employee.objects.get(first_name="JAIRO JAVIER", last_name="SANCHEZ TRIANA")
        print(f"👤 Empleado encontrado: {employee.first_name} {employee.last_name}")
        
        # Verificar perfil facial
        try:
            profile = employee.facial_profile
            print(f"📋 Perfil facial: Activo (Umbral: {profile.confidence_threshold})")
        except FacialRecognitionProfile.DoesNotExist:
            print("⚠️ No hay perfil facial registrado")
        
        # Verificar registros de hoy
        today = timezone.now().date()
        today_records = AttendanceRecord.objects.filter(
            employee=employee,
            timestamp__date=today
        ).order_by('timestamp')
        
        print(f"\n📊 Registros de hoy ({today}):")
        if today_records.exists():
            for record in today_records:
                print(f"   {record.timestamp.strftime('%H:%M:%S')} - {record.get_attendance_type_display()}")
                print(f"   Método: {record.get_verification_method_display()}")
                print(f"   Confianza: {record.facial_confidence}%")
                print(f"   Ubicación: {record.address}")
                print(f"   Válido: {'✅' if record.is_valid else '❌'}")
                print("-" * 30)
        else:
            print("   No hay registros para hoy")
        
        # Determinar próxima acción
        if not today_records.exists():
            next_action = 'IN'
        else:
            last_record = today_records.last()
            next_action = 'OUT' if last_record.attendance_type == 'IN' else 'IN'
        
        print(f"\n🎯 Próxima acción esperada: {next_action}")
        print(f"🚨 Modo de emergencia: {'ACTIVO' if profile.face_encoding == 'EMERGENCY_MODE_ALWAYS_APPROVE' else 'INACTIVO'}")
        
        print("\n✅ SISTEMA LISTO PARA PROBAR")
        print("📱 Ve a: /asistencia/marcar/")
        print("🎯 El sistema debería funcionar automáticamente")
        
    except Employee.DoesNotExist:
        print("❌ Empleado no encontrado")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_emergency_mode()
