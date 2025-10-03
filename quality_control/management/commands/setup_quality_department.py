"""
Comando para crear el Departamento de Control de Calidad con sus puestos
"""
from django.core.management.base import BaseCommand
from departments.models import Department
from positions.models import Position


class Command(BaseCommand):
    help = 'Crea el Departamento de Control de Calidad con sus puestos de trabajo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🏢 Creando Departamento de Control de Calidad...'))
        
        # Crear departamento
        department = self.create_department()
        
        # Crear puestos
        self.create_positions(department)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Departamento de Control de Calidad creado exitosamente!'))
        self.stdout.write(self.style.SUCCESS('📊 Ahora puedes asignar empleados a este departamento'))

    def create_department(self):
        """Crear el departamento de Control de Calidad"""
        self.stdout.write('\n📋 Creando departamento...')
        
        department, created = Department.objects.get_or_create(
            name='Control de Calidad',
            defaults={
                'code': 'CC',
                'description': 'Departamento encargado de la gestión de riesgos, control de calidad, '
                              'auditorías internas, cumplimiento normativo y mejora continua de procesos. '
                              'Responsable de identificar, evaluar y mitigar riesgos operativos, tecnológicos, '
                              'de capital humano, del entorno y reputacionales.',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Departamento creado: {department.name} ({department.code})')
        else:
            self.stdout.write(f'  ⏭️  Departamento ya existe: {department.name}')
        
        return department

    def create_positions(self, department):
        """Crear los puestos del departamento de Control de Calidad"""
        self.stdout.write('\n👥 Creando puestos de trabajo...')
        
        positions = [
            {
                'title': 'Director de Control de Calidad',
                'code': 'DIR-CC',
                'description': 'Responsable de liderar el departamento de Control de Calidad. '
                              'Define estrategias de gestión de riesgos, supervisa auditorías, '
                              'reporta a la alta dirección y asegura el cumplimiento normativo. '
                              'Requiere: Título universitario en Administración, Ingeniería Industrial o afines. '
                              'Mínimo 5 años de experiencia en gestión de calidad y riesgos. '
                              'Certificaciones ISO 9001, ISO 31000 o similares.',
                'level': 'DIRECTOR',
                'employment_type': 'FULL_TIME',
                'min_salary': 2500.00,
                'max_salary': 4000.00,
                'max_positions': 1,
            },
            {
                'title': 'Analista de Riesgos Senior',
                'code': 'ANL-RSG-SR',
                'description': 'Identifica, evalúa y analiza riesgos operativos, tecnológicos y estratégicos. '
                              'Desarrolla matrices de riesgos, propone medidas de control y realiza evaluaciones periódicas. '
                              'Requiere: Título universitario en Administración de Riesgos, Finanzas o Ingeniería. '
                              '3-5 años de experiencia en análisis de riesgos.',
                'level': 'MANAGER',
                'employment_type': 'FULL_TIME',
                'min_salary': 1800.00,
                'max_salary': 2800.00,
                'max_positions': 2,
            },
            {
                'title': 'Analista de Riesgos Junior',
                'code': 'ANL-RSG-JR',
                'description': 'Apoya en la identificación y documentación de riesgos. '
                              'Recopila datos, actualiza matrices de riesgos y asiste en evaluaciones. '
                              'Requiere: Título universitario en Administración, Economía o Ingeniería. '
                              '1-2 años de experiencia.',
                'level': 'JUNIOR',
                'employment_type': 'FULL_TIME',
                'min_salary': 1200.00,
                'max_salary': 1800.00,
                'max_positions': 3,
            },
            {
                'title': 'Auditor de Calidad',
                'code': 'AUD-CAL',
                'description': 'Realiza auditorías internas de procesos y procedimientos. '
                              'Verifica cumplimiento de estándares de calidad, identifica no conformidades. '
                              'Requiere: Título universitario en Ingeniería Industrial o Administración. '
                              '2-4 años de experiencia en auditorías.',
                'level': 'SENIOR',
                'employment_type': 'FULL_TIME',
                'min_salary': 1400.00,
                'max_salary': 2200.00,
                'max_positions': 2,
            },
            {
                'title': 'Especialista en Cumplimiento Normativo',
                'code': 'ESP-NORM',
                'description': 'Asegura el cumplimiento de normativas legales y regulatorias. '
                              'Monitorea cambios legislativos, actualiza políticas internas. '
                              'Requiere: Título universitario en Derecho, Administración o Ingeniería. '
                              '2-3 años de experiencia en cumplimiento.',
                'level': 'SENIOR',
                'employment_type': 'FULL_TIME',
                'min_salary': 1600.00,
                'max_salary': 2400.00,
                'max_positions': 1,
            },
            {
                'title': 'Coordinador de Mejora Continua',
                'code': 'COORD-MC',
                'description': 'Lidera iniciativas de mejora continua y optimización de procesos. '
                              'Implementa metodologías Lean, Six Sigma y Kaizen. '
                              'Requiere: Título universitario en Ingeniería Industrial. '
                              '2-4 años de experiencia en mejora de procesos.',
                'level': 'LEAD',
                'employment_type': 'FULL_TIME',
                'min_salary': 1500.00,
                'max_salary': 2300.00,
                'max_positions': 1,
            },
            {
                'title': 'Asistente de Control de Calidad',
                'code': 'ASIST-CC',
                'description': 'Brinda soporte administrativo al departamento. '
                              'Gestiona documentación, actualiza registros, coordina reuniones. '
                              'Requiere: Título técnico o universitario en curso. '
                              '1 año de experiencia en asistencia administrativa.',
                'level': 'ENTRY',
                'employment_type': 'FULL_TIME',
                'min_salary': 800.00,
                'max_salary': 1200.00,
                'max_positions': 2,
            },
        ]
        
        for pos_data in positions:
            pos_data['department'] = department
            position, created = Position.objects.get_or_create(
                code=pos_data['code'],
                defaults=pos_data
            )
            if created:
                self.stdout.write(f'  ✓ Creado: {position.title} ({position.code}) - Nivel: {position.get_level_display()}')
            else:
                self.stdout.write(f'  ⏭️  Ya existe: {position.title}')
        
        self.stdout.write(f'\n📊 Total de puestos creados: {len(positions)}')
