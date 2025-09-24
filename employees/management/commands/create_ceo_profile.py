"""
Comando Django para crear perfil CEO para el superusuario jairo
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee
from departments.models import Department
from positions.models import Position
from datetime import date

class Command(BaseCommand):
    help = 'Crea perfil de empleado CEO para el superusuario jairo'

    def handle(self, *args, **options):
        try:
            # Obtener el usuario jairo
            user = User.objects.get(username='jairo')
            self.stdout.write(f"✅ Usuario encontrado: {user.username}")
            
            # Verificar si ya tiene perfil
            try:
                existing = Employee.objects.get(user=user)
                self.stdout.write(f"⚠️ Ya existe perfil: {existing.employee_id}")
                return
            except Employee.DoesNotExist:
                pass
            
            # Obtener departamento de Administración
            try:
                department = Department.objects.get(code='ADM')
                self.stdout.write(f"✅ Departamento encontrado: {department.name}")
            except Department.DoesNotExist:
                self.stdout.write("❌ Departamento ADM no encontrado")
                return
            
            # Buscar posición de DIRECTOR
            try:
                position = Position.objects.filter(level='DIRECTOR').first()
                if not position:
                    # Si no hay DIRECTOR, buscar MANAGER
                    position = Position.objects.filter(level='MANAGER').first()
                if not position:
                    self.stdout.write("❌ No se encontró posición de alto rango")
                    return
                self.stdout.write(f"✅ Posición encontrada: {position.title}")
            except Exception as e:
                self.stdout.write(f"❌ Error buscando posición: {e}")
                return
            
            # Crear perfil de empleado
            employee = Employee.objects.create(
                user=user,
                employee_id='CEO001',
                first_name='Jairo',
                last_name='Sánchez Triana',
                email='jairo1991st@hotmail.com',
                phone='+593-99-123-4567',
                national_id='1234567890',
                # Campos opcionales que pueden ser null
                date_of_birth=date(1991, 1, 1) if hasattr(Employee._meta.get_field('date_of_birth'), 'null') else None,
                gender='M',
                marital_status='SINGLE',
                address='Av. Principal 123, Centro Empresarial',
                city='Guayaquil',
                country='Ecuador',
                department=department,
                position=position,
                hire_date=date(2024, 1, 1),
                current_salary=8000.00,
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"🎉 Perfil CEO creado exitosamente: {employee.employee_id} - {employee.get_full_name()}"
                )
            )
            self.stdout.write(f"📊 Nivel de permisos: {employee.get_permission_level()}")
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Usuario 'jairo' no encontrado"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
