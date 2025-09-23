"""
Comando Django para crear perfil de empleado para el usuario admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee
from departments.models import Department
from positions.models import Position

class Command(BaseCommand):
    help = 'Crear perfil de empleado para el usuario admin'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Verificando y creando perfil de empleado para admin...")
        
        try:
            # Obtener usuario admin
            admin_user = User.objects.get(username='admin')
            self.stdout.write(f"✅ Usuario admin encontrado: {admin_user.email}")
            
            # Verificar si ya tiene perfil de empleado
            try:
                employee = Employee.objects.get(user=admin_user)
                self.stdout.write(f"✅ Perfil de empleado ya existe: {employee.get_full_name()}")
                self.stdout.write(f"   - Departamento: {employee.department.name if employee.department else 'Sin departamento'}")
                self.stdout.write(f"   - Posición: {employee.position.title if employee.position else 'Sin posición'}")
                return
            except Employee.DoesNotExist:
                self.stdout.write("⚠️ No existe perfil de empleado para admin, creando...")
            
            # Obtener departamento administrativo
            try:
                admin_dept = Department.objects.get(code='ADM')
                self.stdout.write(f"✅ Departamento administrativo encontrado: {admin_dept.name}")
            except Department.DoesNotExist:
                self.stdout.write("❌ Departamento administrativo no encontrado, creando...")
                admin_dept = Department.objects.create(
                    name='Administración',
                    code='ADM',
                    description='Departamento de Administración General',
                    department_type='ADMINISTRATIVE'
                )
                self.stdout.write(f"✅ Departamento creado: {admin_dept.name}")
            
            # Obtener posición de director
            try:
                director_position = Position.objects.filter(level='DIRECTOR').first()
                if not director_position:
                    self.stdout.write("❌ Posición de director no encontrada, creando...")
                    director_position = Position.objects.create(
                        title='Director General',
                        code='DIR-GEN-001',
                        department=admin_dept,
                        level='DIRECTOR',
                        employment_type='FULL_TIME',
                        description='Director General de la empresa'
                    )
                    self.stdout.write(f"✅ Posición creada: {director_position.title}")
                else:
                    self.stdout.write(f"✅ Posición de director encontrada: {director_position.title}")
            except Exception as e:
                self.stdout.write(f"❌ Error obteniendo posición: {e}")
                return
            
            # Crear perfil de empleado para admin
            employee = Employee.objects.create(
                user=admin_user,
                employee_id='EMP-ADMIN-001',
                first_name=admin_user.first_name or 'Administrador',
                last_name=admin_user.last_name or 'Sistema',
                email=admin_user.email,
                department=admin_dept,
                position=director_position,
                phone='0999999999',
                address='Oficina Principal',
                hire_date='2024-01-01',
                is_active=True
            )
            
            self.stdout.write(f"✅ Perfil de empleado creado exitosamente:")
            self.stdout.write(f"   - ID: {employee.employee_id}")
            self.stdout.write(f"   - Nombre: {employee.get_full_name()}")
            self.stdout.write(f"   - Email: {employee.email}")
            self.stdout.write(f"   - Departamento: {employee.department.name}")
            self.stdout.write(f"   - Posición: {employee.position.title}")
            self.stdout.write(f"   - Nivel: {employee.position.level}")
            
            # Verificar permisos
            self.stdout.write(f"\n🔐 Verificando permisos:")
            self.stdout.write(f"   - Nivel de permisos: {employee.get_permission_level()}")
            self.stdout.write(f"   - Es superusuario: {admin_user.is_superuser}")
            self.stdout.write(f"   - Es staff: {admin_user.is_staff}")
            
            self.stdout.write(f"\n✅ ¡Perfil de empleado configurado correctamente!")
            self.stdout.write(f"   Ahora el GPS tracking debería funcionar para el usuario admin.")
            
        except User.DoesNotExist:
            self.stdout.write("❌ Usuario admin no encontrado")
            self.stdout.write("   Ejecuta primero: python manage.py createsuperuser")
        except Exception as e:
            self.stdout.write(f"❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
