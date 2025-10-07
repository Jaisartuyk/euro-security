"""
Script para habilitar acceso al Centro de Operaciones
Ejecutar: python enable_operations_access.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

def enable_operations_access(username_or_email):
    """Habilita acceso al Centro de Operaciones para un usuario"""
    
    try:
        # Buscar usuario
        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            user = User.objects.get(email=username_or_email)
        
        print(f"\n✅ Usuario encontrado: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Nombre: {user.get_full_name()}")
        
        # Verificar si tiene perfil de empleado
        try:
            employee = user.employee
            print(f"   Puesto: {employee.position}")
            print(f"   Departamento: {employee.department}")
        except:
            print("   ⚠️ No tiene perfil de empleado")
        
        # Dar permisos de staff
        if not user.is_staff:
            user.is_staff = True
            user.save()
            print(f"\n✅ Permisos de STAFF otorgados")
        else:
            print(f"\n✅ Ya tiene permisos de STAFF")
        
        # Verificar permisos
        print(f"\n📋 Estado de permisos:")
        print(f"   is_staff: {user.is_staff} {'✅' if user.is_staff else '❌'}")
        print(f"   is_superuser: {user.is_superuser} {'✅' if user.is_superuser else '❌'}")
        print(f"   is_active: {user.is_active} {'✅' if user.is_active else '❌'}")
        
        print(f"\n🎯 Ahora puede acceder a:")
        print(f"   • Centro de Operaciones: /asistencia/operaciones/")
        print(f"   • Analytics: /asistencia/operaciones/analytics/")
        print(f"   • Admin Django: /admin/")
        
        return True
        
    except User.DoesNotExist:
        print(f"\n❌ Usuario no encontrado: {username_or_email}")
        print(f"\n💡 Usuarios disponibles:")
        for u in User.objects.all()[:10]:
            print(f"   - {u.username} ({u.email})")
        return False
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("🔐 HABILITAR ACCESO AL CENTRO DE OPERACIONES")
    print("=" * 60)
    
    # Solicitar usuario
    username = input("\n👤 Ingresa tu username o email: ").strip()
    
    if username:
        enable_operations_access(username)
    else:
        print("\n❌ Debes ingresar un username o email")
    
    print("\n" + "=" * 60)
