"""
Comando para crear usuarios para empleados existentes que no tienen cuenta
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee


class Command(BaseCommand):
    help = 'Crea usuarios para empleados existentes que no tienen cuenta'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Crear usuarios para todos los empleados sin cuenta',
        )
        parser.add_argument(
            '--employee-id',
            type=str,
            help='Crear usuario para un empleado específico por ID',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué se haría sin realizar cambios',
        )

    def handle(self, *args, **options):
        if options['all']:
            employees = Employee.objects.filter(user__isnull=True, is_active=True)
            self.stdout.write(f"Encontrados {employees.count()} empleados sin cuenta de usuario")
            
            created_users = []
            
            for employee in employees:
                if options['dry_run']:
                    self.stdout.write(f"[DRY RUN] Crearía usuario para: {employee.get_full_name()} ({employee.employee_id})")
                else:
                    credentials = employee.create_user_account()
                    if credentials:
                        created_users.append({
                            'employee': employee,
                            'credentials': credentials
                        })
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Usuario creado para {employee.get_full_name()}: {credentials['username']}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠ No se pudo crear usuario para {employee.get_full_name()}"
                            )
                        )
            
            if not options['dry_run'] and created_users:
                self.stdout.write("\n" + "="*60)
                self.stdout.write(self.style.SUCCESS("RESUMEN DE CREDENCIALES CREADAS"))
                self.stdout.write("="*60)
                
                for item in created_users:
                    employee = item['employee']
                    credentials = item['credentials']
                    self.stdout.write(f"Empleado: {employee.get_full_name()}")
                    self.stdout.write(f"ID: {employee.employee_id}")
                    self.stdout.write(f"Usuario: {credentials['username']}")
                    self.stdout.write(f"Contraseña: {credentials['password']}")
                    self.stdout.write(f"Nivel: {employee.get_permission_level()}")
                    self.stdout.write("-" * 40)
                
                self.stdout.write(
                    self.style.WARNING(
                        "\n⚠ IMPORTANTE: Guarda estas credenciales de forma segura. "
                        "No se mostrarán nuevamente."
                    )
                )
        
        elif options['employee_id']:
            try:
                employee = Employee.objects.get(employee_id=options['employee_id'])
                
                if employee.user:
                    self.stdout.write(
                        self.style.WARNING(
                            f"El empleado {employee.get_full_name()} ya tiene una cuenta de usuario: {employee.user.username}"
                        )
                    )
                    return
                
                if options['dry_run']:
                    self.stdout.write(f"[DRY RUN] Crearía usuario para: {employee.get_full_name()}")
                else:
                    credentials = employee.create_user_account()
                    if credentials:
                        self.stdout.write("\n" + "="*50)
                        self.stdout.write(self.style.SUCCESS("CREDENCIALES CREADAS"))
                        self.stdout.write("="*50)
                        self.stdout.write(f"Empleado: {employee.get_full_name()}")
                        self.stdout.write(f"ID: {employee.employee_id}")
                        self.stdout.write(f"Usuario: {credentials['username']}")
                        self.stdout.write(f"Contraseña: {credentials['password']}")
                        self.stdout.write(f"Nivel: {employee.get_permission_level()}")
                        self.stdout.write(
                            self.style.WARNING(
                                "\n⚠ IMPORTANTE: Guarda estas credenciales de forma segura."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"✗ No se pudo crear usuario para {employee.get_full_name()}"
                            )
                        )
                        
            except Employee.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ No se encontró empleado con ID: {options['employee_id']}"
                    )
                )
        
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Debes especificar --all o --employee-id. Usa --help para más información."
                )
            )

    def show_statistics(self):
        """Muestra estadísticas de empleados y usuarios"""
        total_employees = Employee.objects.filter(is_active=True).count()
        employees_with_users = Employee.objects.filter(user__isnull=False, is_active=True).count()
        employees_without_users = total_employees - employees_with_users
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("ESTADÍSTICAS DE USUARIOS")
        self.stdout.write("="*50)
        self.stdout.write(f"Total empleados activos: {total_employees}")
        self.stdout.write(f"Con cuenta de usuario: {employees_with_users}")
        self.stdout.write(f"Sin cuenta de usuario: {employees_without_users}")
        
        if employees_without_users > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"\n⚠ Hay {employees_without_users} empleados sin cuenta de usuario."
                )
            )
            self.stdout.write("Ejecuta: python manage.py create_employee_users --all")
