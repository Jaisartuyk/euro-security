from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from departments.models import Department
from positions.models import Position
from employees.models import Employee
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Crea datos de ejemplo para EURO SECURITY'

    def handle(self, *args, **options):
        self.stdout.write('Creando datos de ejemplo para EURO SECURITY...')
        
        # Crear departamentos específicos para empresa de seguridad
        departments_data = [
            {
                'name': 'Operaciones de Seguridad', 
                'code': 'OPS-SEC', 
                'type': 'OPERACIONES',
                'budget': 500000,
                'description': 'Personal operativo de seguridad física, guardias y supervisores de campo'
            },
            {
                'name': 'Administración', 
                'code': 'ADMIN', 
                'type': 'ADMINISTRACION',
                'budget': 120000,
                'description': 'Recursos humanos, contabilidad, facturación y gestión administrativa'
            },
            {
                'name': 'Comercial y Ventas', 
                'code': 'COMERCIAL', 
                'type': 'COMERCIAL',
                'budget': 200000,
                'description': 'Ventas, atención al cliente, marketing y desarrollo de negocios'
            },
            {
                'name': 'Soporte Técnico', 
                'code': 'SOPORTE', 
                'type': 'SOPORTE',
                'budget': 150000,
                'description': 'Sistemas de alarmas, CCTV, control de acceso y tecnología de seguridad'
            },
            {
                'name': 'Dirección General', 
                'code': 'DIRECCION', 
                'type': 'DIRECCION',
                'budget': 250000,
                'description': 'Dirección ejecutiva y gerencia general'
            },
            {
                'name': 'Finanzas', 
                'code': 'FIN', 
                'type': 'FINANZAS',
                'budget': 180000,
                'description': 'Gestión financiera y contabilidad'
            },
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'department_type': dept_data['type'],
                    'budget': dept_data['budget'],
                    'description': f'Departamento de {dept_data["name"]} de EURO SECURITY',
                    'is_active': True
                }
            )
            departments[dept_data['code']] = dept
            if created:
                self.stdout.write(f'✓ Departamento creado: {dept.name}')
        
        # Crear puestos de trabajo específicos para empresa de seguridad
        positions_data = [
            # DIRECCIÓN GENERAL
            {'title': 'Director General', 'code': 'DIR-GEN', 'dept': 'DIRECCION', 'level': 'DIRECTOR', 'min_sal': 60000, 'max_sal': 80000},
            {'title': 'Gerente General', 'code': 'GER-GEN', 'dept': 'DIRECCION', 'level': 'MANAGER', 'min_sal': 45000, 'max_sal': 60000},
            
            # OPERACIONES DE SEGURIDAD (Personal Operativo)
            {'title': 'Director de Operaciones', 'code': 'DIR-OPS', 'dept': 'OPS-SEC', 'level': 'DIRECTOR', 'min_sal': 50000, 'max_sal': 70000},
            {'title': 'Gerente de Operaciones', 'code': 'GER-OPS', 'dept': 'OPS-SEC', 'level': 'MANAGER', 'min_sal': 40000, 'max_sal': 55000},
            
            # Supervisores y Líderes de Turno
            {'title': 'Supervisor de Turno Nocturno', 'code': 'SUP-NOC', 'dept': 'OPS-SEC', 'level': 'LEAD', 'min_sal': 28000, 'max_sal': 38000},
            {'title': 'Supervisor de Turno Diurno', 'code': 'SUP-DIA', 'dept': 'OPS-SEC', 'level': 'LEAD', 'min_sal': 28000, 'max_sal': 38000},
            {'title': 'Coordinador de Zona', 'code': 'COORD-ZONA', 'dept': 'OPS-SEC', 'level': 'LEAD', 'min_sal': 25000, 'max_sal': 35000},
            
            # Guardias Senior y Especializados
            {'title': 'Guardia de Seguridad III (Senior)', 'code': 'GUA-III', 'dept': 'OPS-SEC', 'level': 'SENIOR', 'min_sal': 22000, 'max_sal': 30000},
            {'title': 'Guardia Especializado en Eventos', 'code': 'GUA-EVE', 'dept': 'OPS-SEC', 'level': 'SENIOR', 'min_sal': 20000, 'max_sal': 28000},
            {'title': 'Operador de CCTV Senior', 'code': 'OP-CCTV-SR', 'dept': 'OPS-SEC', 'level': 'SENIOR', 'min_sal': 18000, 'max_sal': 25000},
            
            # Guardias Regulares
            {'title': 'Guardia de Seguridad II', 'code': 'GUA-II', 'dept': 'OPS-SEC', 'level': 'JUNIOR', 'min_sal': 16000, 'max_sal': 22000},
            {'title': 'Guardia de Patrullaje Móvil', 'code': 'GUA-PAT', 'dept': 'OPS-SEC', 'level': 'JUNIOR', 'min_sal': 15000, 'max_sal': 21000},
            {'title': 'Operador de CCTV', 'code': 'OP-CCTV', 'dept': 'OPS-SEC', 'level': 'JUNIOR', 'min_sal': 14000, 'max_sal': 20000},
            
            # Guardias Básicos
            {'title': 'Guardia de Seguridad I', 'code': 'GUA-I', 'dept': 'OPS-SEC', 'level': 'ENTRY', 'min_sal': 12000, 'max_sal': 16000},
            {'title': 'Guardia de Acceso', 'code': 'GUA-ACC', 'dept': 'OPS-SEC', 'level': 'ENTRY', 'min_sal': 12000, 'max_sal': 16000},
            {'title': 'Vigilante Nocturno', 'code': 'VIG-NOC', 'dept': 'OPS-SEC', 'level': 'ENTRY', 'min_sal': 12000, 'max_sal': 16000},
            
            # ADMINISTRACIÓN
            {'title': 'Gerente Administrativo', 'code': 'GER-ADM', 'dept': 'ADMIN', 'level': 'MANAGER', 'min_sal': 35000, 'max_sal': 48000},
            {'title': 'Jefe de Recursos Humanos', 'code': 'JEF-RRHH', 'dept': 'ADMIN', 'level': 'LEAD', 'min_sal': 30000, 'max_sal': 40000},
            {'title': 'Especialista en Nómina', 'code': 'ESP-NOM', 'dept': 'ADMIN', 'level': 'SENIOR', 'min_sal': 22000, 'max_sal': 30000},
            {'title': 'Asistente de RRHH', 'code': 'AST-RRHH', 'dept': 'ADMIN', 'level': 'JUNIOR', 'min_sal': 15000, 'max_sal': 22000},
            {'title': 'Recepcionista', 'code': 'RECEP', 'dept': 'ADMIN', 'level': 'ENTRY', 'min_sal': 12000, 'max_sal': 16000},
            
            # COMERCIAL Y VENTAS
            {'title': 'Gerente Comercial', 'code': 'GER-COM', 'dept': 'COMERCIAL', 'level': 'MANAGER', 'min_sal': 40000, 'max_sal': 55000},
            {'title': 'Ejecutivo de Ventas Senior', 'code': 'EJEC-VEN-SR', 'dept': 'COMERCIAL', 'level': 'SENIOR', 'min_sal': 25000, 'max_sal': 35000},
            {'title': 'Ejecutivo de Ventas', 'code': 'EJEC-VEN', 'dept': 'COMERCIAL', 'level': 'JUNIOR', 'min_sal': 18000, 'max_sal': 25000},
            {'title': 'Atención al Cliente', 'code': 'AT-CLI', 'dept': 'COMERCIAL', 'level': 'JUNIOR', 'min_sal': 15000, 'max_sal': 20000},
            
            # SOPORTE TÉCNICO
            {'title': 'Jefe de Soporte Técnico', 'code': 'JEF-SOP', 'dept': 'SOPORTE', 'level': 'MANAGER', 'min_sal': 38000, 'max_sal': 50000},
            {'title': 'Técnico en Alarmas Senior', 'code': 'TEC-ALA-SR', 'dept': 'SOPORTE', 'level': 'SENIOR', 'min_sal': 25000, 'max_sal': 35000},
            {'title': 'Técnico en CCTV', 'code': 'TEC-CCTV', 'dept': 'SOPORTE', 'level': 'JUNIOR', 'min_sal': 18000, 'max_sal': 25000},
            {'title': 'Técnico en Control de Acceso', 'code': 'TEC-ACC', 'dept': 'SOPORTE', 'level': 'JUNIOR', 'min_sal': 18000, 'max_sal': 25000},
            
            # FINANZAS
            {'title': 'Director Financiero', 'code': 'DIR-FIN', 'dept': 'FIN', 'level': 'DIRECTOR', 'min_sal': 50000, 'max_sal': 70000},
            {'title': 'Contador General', 'code': 'CONT-GEN', 'dept': 'FIN', 'level': 'SENIOR', 'min_sal': 25000, 'max_sal': 35000},
            {'title': 'Auxiliar Contable', 'code': 'AUX-CONT', 'dept': 'FIN', 'level': 'JUNIOR', 'min_sal': 15000, 'max_sal': 22000},
        ]
        
        positions = {}
        for pos_data in positions_data:
            pos, created = Position.objects.get_or_create(
                code=pos_data['code'],
                defaults={
                    'title': pos_data['title'],
                    'department': departments[pos_data['dept']],
                    'level': pos_data['level'],
                    'employment_type': 'FULL_TIME',
                    'min_salary': pos_data['min_sal'],
                    'max_salary': pos_data['max_sal'],
                    'description': f'Puesto de {pos_data["title"]} en el departamento de {departments[pos_data["dept"]].name}',
                    'max_positions': random.randint(1, 5),
                    'is_active': True,
                    'is_hiring': random.choice([True, False])
                }
            )
            positions[pos_data['code']] = pos
            if created:
                self.stdout.write(f'✓ Puesto creado: {pos.title}')
        
        # Crear empleados de ejemplo con nueva estructura
        employees_data = [
            # DIRECCIÓN GENERAL
            {'first': 'Carlos', 'last': 'Rodríguez', 'email': 'carlos.rodriguez@eurosecurity.com', 'pos': 'DIR-GEN', 'id': '12345678', 'phone': '555-0101'},
            {'first': 'María', 'last': 'González', 'email': 'maria.gonzalez@eurosecurity.com', 'pos': 'GER-GEN', 'id': '23456789', 'phone': '555-0102'},
            
            # DIRECTORES DEPARTAMENTALES
            {'first': 'José', 'last': 'Martínez', 'email': 'jose.martinez@eurosecurity.com', 'pos': 'DIR-FIN', 'id': '34567890', 'phone': '555-0103'},
            {'first': 'Ana', 'last': 'López', 'email': 'ana.lopez@eurosecurity.com', 'pos': 'DIR-OPS', 'id': '45678901', 'phone': '555-0104'},
            
            # GERENTES
            {'first': 'Pedro', 'last': 'Sánchez', 'email': 'pedro.sanchez@eurosecurity.com', 'pos': 'GER-OPS', 'id': '56789012', 'phone': '555-0105'},
            {'first': 'Laura', 'last': 'Herrera', 'email': 'laura.herrera@eurosecurity.com', 'pos': 'GER-ADM', 'id': '67890123', 'phone': '555-0106'},
            {'first': 'Roberto', 'last': 'Jiménez', 'email': 'roberto.jimenez@eurosecurity.com', 'pos': 'GER-COM', 'id': '90123456', 'phone': '555-0109'},
            
            # SUPERVISORES Y LÍDERES
            {'first': 'Miguel', 'last': 'Torres', 'email': 'miguel.torres@eurosecurity.com', 'pos': 'SUP-NOC', 'id': '78901234', 'phone': '555-0107'},
            {'first': 'Carmen', 'last': 'Ruiz', 'email': 'carmen.ruiz@eurosecurity.com', 'pos': 'SUP-DIA', 'id': '89012345', 'phone': '555-0108'},
            {'first': 'Elena', 'last': 'Morales', 'email': 'elena.morales@eurosecurity.com', 'pos': 'COORD-ZONA', 'id': '01234567', 'phone': '555-0110'},
            {'first': 'Ricardo', 'last': 'Vega', 'email': 'ricardo.vega@eurosecurity.com', 'pos': 'JEF-RRHH', 'id': '11134567', 'phone': '555-0117'},
            {'first': 'Sandra', 'last': 'Peña', 'email': 'sandra.pena@eurosecurity.com', 'pos': 'JEF-SOP', 'id': '11234568', 'phone': '555-0118'},
            
            # GUARDIAS SENIOR Y ESPECIALIZADOS
            {'first': 'Fernando', 'last': 'Castro', 'email': 'fernando.castro@eurosecurity.com', 'pos': 'GUA-III', 'id': '11234567', 'phone': '555-0111'},
            {'first': 'Claudia', 'last': 'Moreno', 'email': 'claudia.moreno@eurosecurity.com', 'pos': 'GUA-EVE', 'id': '12234567', 'phone': '555-0119'},
            {'first': 'Javier', 'last': 'Ramos', 'email': 'javier.ramos@eurosecurity.com', 'pos': 'OP-CCTV-SR', 'id': '13234567', 'phone': '555-0120'},
            
            # GUARDIAS REGULARES
            {'first': 'Isabel', 'last': 'Vega', 'email': 'isabel.vega@eurosecurity.com', 'pos': 'GUA-II', 'id': '21234567', 'phone': '555-0112'},
            {'first': 'Andrés', 'last': 'Mendoza', 'email': 'andres.mendoza@eurosecurity.com', 'pos': 'GUA-PAT', 'id': '31234567', 'phone': '555-0113'},
            {'first': 'Patricia', 'last': 'Ramírez', 'email': 'patricia.ramirez@eurosecurity.com', 'pos': 'OP-CCTV', 'id': '41234567', 'phone': '555-0114'},
            
            # GUARDIAS BÁSICOS
            {'first': 'Luis', 'last': 'García', 'email': 'luis.garcia@eurosecurity.com', 'pos': 'GUA-I', 'id': '51234567', 'phone': '555-0115'},
            {'first': 'María', 'last': 'Fernández', 'email': 'maria.fernandez@eurosecurity.com', 'pos': 'GUA-ACC', 'id': '61234567', 'phone': '555-0116'},
            {'first': 'Carlos', 'last': 'Herrera', 'email': 'carlos.herrera@eurosecurity.com', 'pos': 'VIG-NOC', 'id': '11334567', 'phone': '555-0121'},
            
            # PERSONAL ADMINISTRATIVO
            {'first': 'Gabriela', 'last': 'Ortiz', 'email': 'gabriela.ortiz@eurosecurity.com', 'pos': 'AST-RRHH', 'id': '11434567', 'phone': '555-0122'},
            {'first': 'Diana', 'last': 'Silva', 'email': 'diana.silva@eurosecurity.com', 'pos': 'ESP-NOM', 'id': '11534567', 'phone': '555-0123'},
            {'first': 'Rosa', 'last': 'Delgado', 'email': 'rosa.delgado@eurosecurity.com', 'pos': 'RECEP', 'id': '11634567', 'phone': '555-0124'},
            
            # PERSONAL COMERCIAL
            {'first': 'Alejandro', 'last': 'Vargas', 'email': 'alejandro.vargas@eurosecurity.com', 'pos': 'EJEC-VEN-SR', 'id': '03234567', 'phone': '555-0125'},
            {'first': 'Natalia', 'last': 'Cruz', 'email': 'natalia.cruz@eurosecurity.com', 'pos': 'EJEC-VEN', 'id': '04234567', 'phone': '555-0126'},
            {'first': 'Paola', 'last': 'Restrepo', 'email': 'paola.restrepo@eurosecurity.com', 'pos': 'AT-CLI', 'id': '05234567', 'phone': '555-0127'},
            
            # PERSONAL TÉCNICO
            {'first': 'Diego', 'last': 'Flores', 'email': 'diego.flores@eurosecurity.com', 'pos': 'TEC-ALA-SR', 'id': '06234567', 'phone': '555-0128'},
            {'first': 'Sergio', 'last': 'Muñoz', 'email': 'sergio.munoz@eurosecurity.com', 'pos': 'TEC-CCTV', 'id': '07234567', 'phone': '555-0129'},
            {'first': 'Andrea', 'last': 'Rojas', 'email': 'andrea.rojas@eurosecurity.com', 'pos': 'TEC-ACC', 'id': '08234567', 'phone': '555-0130'},
            
            # PERSONAL FINANCIERO
            {'first': 'Jaime', 'last': 'Ospina', 'email': 'jaime.ospina@eurosecurity.com', 'pos': 'CONT-GEN', 'id': '09234567', 'phone': '555-0131'},
            {'first': 'Liliana', 'last': 'Castañeda', 'email': 'liliana.castaneda@eurosecurity.com', 'pos': 'AUX-CONT', 'id': '10234567', 'phone': '555-0132'},
        ]
        
        for emp_data in employees_data:
            position = positions[emp_data['pos']]
            
            # Calcular salario aleatorio dentro del rango del puesto
            salary = random.randint(int(position.min_salary), int(position.max_salary))
            
            # Fecha de contratación aleatoria en los últimos 2 años
            days_ago = random.randint(30, 730)
            hire_date = date.today() - timedelta(days=days_ago)
            
            # Fecha de nacimiento (entre 25 y 55 años)
            age = random.randint(25, 55)
            birth_date = date.today() - timedelta(days=age*365 + random.randint(0, 365))
            
            emp, created = Employee.objects.get_or_create(
                email=emp_data['email'],
                defaults={
                    'first_name': emp_data['first'],
                    'last_name': emp_data['last'],
                    'national_id': emp_data['id'],
                    'phone': emp_data['phone'],
                    'date_of_birth': birth_date,
                    'gender': random.choice(['M', 'F']),
                    'marital_status': random.choice(['SINGLE', 'MARRIED', 'DIVORCED']),
                    'address': f'Calle {random.randint(1, 100)} #{random.randint(100, 999)}',
                    'city': random.choice(['Ciudad de México', 'Guadalajara', 'Monterrey', 'Puebla', 'Tijuana']),
                    'country': 'México',
                    'department': position.department,
                    'position': position,
                    'hire_date': hire_date,
                    'current_salary': salary,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'✓ Empleado creado: {emp.get_full_name()} - {emp.position.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n¡Datos de ejemplo creados exitosamente para EURO SECURITY!\n'
                f'- {Department.objects.count()} departamentos\n'
                f'- {Position.objects.count()} puestos de trabajo\n'
                f'- {Employee.objects.count()} empleados\n'
            )
        )
