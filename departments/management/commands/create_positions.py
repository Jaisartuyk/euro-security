from django.core.management.base import BaseCommand
from departments.models import Department
from positions.models import Position


class Command(BaseCommand):
    help = 'Crear puestos de trabajo para EURO SECURITY'

    def handle(self, *args, **options):
        self.stdout.write('💼 CREANDO PUESTOS DE TRABAJO PARA EURO SECURITY')
        self.stdout.write('=' * 60)
        
        # Obtener departamentos
        departments = {dept.name: dept for dept in Department.objects.all()}
        
        if not departments:
            self.stdout.write(self.style.ERROR('❌ No hay departamentos creados'))
            return
        
        # Puestos por departamento
        positions_data = [
            # ADMINISTRACIÓN
            {'department': 'Administración', 'name': 'Director General', 'description': 'Dirección ejecutiva de la empresa', 'salary_min': 8000, 'salary_max': 12000},
            {'department': 'Administración', 'name': 'Gerente General', 'description': 'Gestión general de operaciones', 'salary_min': 6000, 'salary_max': 8000},
            {'department': 'Administración', 'name': 'Asistente Ejecutivo', 'description': 'Apoyo administrativo ejecutivo', 'salary_min': 1200, 'salary_max': 1800},
            
            # RECURSOS HUMANOS
            {'department': 'Recursos Humanos', 'name': 'Jefe de RRHH', 'description': 'Dirección del departamento de recursos humanos', 'salary_min': 3500, 'salary_max': 5000},
            {'department': 'Recursos Humanos', 'name': 'Analista de RRHH', 'description': 'Gestión de personal y nómina', 'salary_min': 1500, 'salary_max': 2500},
            {'department': 'Recursos Humanos', 'name': 'Especialista en Capacitación', 'description': 'Desarrollo y capacitación del personal', 'salary_min': 1800, 'salary_max': 2800},
            
            # SEGURIDAD FÍSICA
            {'department': 'Seguridad Física', 'name': 'Jefe de Seguridad', 'description': 'Coordinación de servicios de seguridad física', 'salary_min': 3000, 'salary_max': 4500},
            {'department': 'Seguridad Física', 'name': 'Supervisor de Turno', 'description': 'Supervisión de guardias por turnos', 'salary_min': 1800, 'salary_max': 2500},
            {'department': 'Seguridad Física', 'name': 'Guardia de Seguridad', 'description': 'Servicios de vigilancia y protección', 'salary_min': 800, 'salary_max': 1200},
            {'department': 'Seguridad Física', 'name': 'Guardia Especializado', 'description': 'Seguridad especializada y escolta', 'salary_min': 1000, 'salary_max': 1500},
            
            # SEGURIDAD ELECTRÓNICA
            {'department': 'Seguridad Electrónica', 'name': 'Jefe de Sistemas', 'description': 'Dirección de sistemas de seguridad electrónica', 'salary_min': 3500, 'salary_max': 5000},
            {'department': 'Seguridad Electrónica', 'name': 'Técnico en CCTV', 'description': 'Instalación y mantenimiento de cámaras', 'salary_min': 1500, 'salary_max': 2200},
            {'department': 'Seguridad Electrónica', 'name': 'Técnico en Alarmas', 'description': 'Sistemas de alarmas y sensores', 'salary_min': 1500, 'salary_max': 2200},
            {'department': 'Seguridad Electrónica', 'name': 'Operador de Monitoreo', 'description': 'Monitoreo de sistemas de seguridad', 'salary_min': 1000, 'salary_max': 1500},
            
            # OPERACIONES
            {'department': 'Operaciones', 'name': 'Gerente de Operaciones', 'description': 'Gestión operativa de servicios', 'salary_min': 4000, 'salary_max': 6000},
            {'department': 'Operaciones', 'name': 'Coordinador de Servicios', 'description': 'Coordinación de servicios al cliente', 'salary_min': 2000, 'salary_max': 3000},
            {'department': 'Operaciones', 'name': 'Despachador', 'description': 'Control y despacho de personal', 'salary_min': 1200, 'salary_max': 1800},
            
            # TECNOLOGÍA
            {'department': 'Tecnología', 'name': 'Jefe de IT', 'description': 'Dirección de tecnología e informática', 'salary_min': 3500, 'salary_max': 5500},
            {'department': 'Tecnología', 'name': 'Desarrollador de Software', 'description': 'Desarrollo de aplicaciones y sistemas', 'salary_min': 2500, 'salary_max': 4000},
            {'department': 'Tecnología', 'name': 'Soporte Técnico', 'description': 'Soporte técnico y mantenimiento', 'salary_min': 1500, 'salary_max': 2500},
            
            # COMERCIAL
            {'department': 'Comercial', 'name': 'Gerente Comercial', 'description': 'Dirección de ventas y marketing', 'salary_min': 3500, 'salary_max': 5000},
            {'department': 'Comercial', 'name': 'Ejecutivo de Ventas', 'description': 'Ventas de servicios de seguridad', 'salary_min': 1500, 'salary_max': 2500},
            {'department': 'Comercial', 'name': 'Atención al Cliente', 'description': 'Servicio y atención al cliente', 'salary_min': 1000, 'salary_max': 1500},
            
            # FINANZAS
            {'department': 'Finanzas', 'name': 'Jefe de Finanzas', 'description': 'Dirección financiera y contable', 'salary_min': 3500, 'salary_max': 5000},
            {'department': 'Finanzas', 'name': 'Contador', 'description': 'Contabilidad y estados financieros', 'salary_min': 2000, 'salary_max': 3000},
            {'department': 'Finanzas', 'name': 'Auxiliar Contable', 'description': 'Apoyo contable y facturación', 'salary_min': 1200, 'salary_max': 1800},
        ]
        
        created_count = 0
        existed_count = 0
        
        for pos_data in positions_data:
            dept_name = pos_data['department']
            
            if dept_name not in departments:
                self.stdout.write(self.style.ERROR(f'❌ Departamento "{dept_name}" no encontrado'))
                continue
                
            dept = departments[dept_name]
            
            # Generar código único para el puesto
            import hashlib
            name_clean = pos_data['name'].replace(' ', '_').upper()
            # Usar hash para garantizar unicidad
            name_hash = hashlib.md5(f"{dept.code}_{pos_data['name']}".encode()).hexdigest()[:4]
            code = f"{dept.code}_{name_clean[:6]}_{name_hash}"
            
            position, created = Position.objects.get_or_create(
                code=code,
                defaults={
                    'title': pos_data['name'],
                    'department': dept,
                    'description': pos_data['description'],
                    'min_salary': pos_data['salary_min'],
                    'max_salary': pos_data['salary_max'],
                    'level': 'SENIOR',  # Nivel por defecto
                    'employment_type': 'FULL_TIME',  # Tiempo completo por defecto
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'✅ {dept.name} → {position.title}')
            else:
                existed_count += 1
                self.stdout.write(f'📋 {dept.name} → {position.title} (ya existe)')
        
        self.stdout.write('\n📊 RESUMEN:')
        self.stdout.write(f'   🏢 Departamentos: {Department.objects.count()}')
        self.stdout.write(f'   💼 Total puestos: {Position.objects.count()}')
        self.stdout.write(f'   ✅ Nuevos puestos: {created_count}')
        self.stdout.write(f'   📋 Puestos existentes: {existed_count}')
        
        self.stdout.write('\n🎯 ESTRUCTURA POR DEPARTAMENTO:')
        for dept in Department.objects.all():
            positions_count = dept.positions.count()
            self.stdout.write(f'   🏢 {dept.name}: {positions_count} puestos')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡PUESTOS CREADOS EXITOSAMENTE!'))
