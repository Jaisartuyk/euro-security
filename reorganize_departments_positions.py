"""
Script de reorganización completa de Departamentos y Puestos
EURO SECURITY - Sistema HR

Elimina duplicados y organiza correctamente la estructura organizacional
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from departments.models import Department
from positions.models import Position
from django.contrib.auth.models import User

def reorganize_departments_and_positions():
    """Reorganiza toda la estructura de departamentos y puestos"""
    
    print("=" * 80)
    print("🏢 REORGANIZACIÓN DE DEPARTAMENTOS Y PUESTOS - EURO SECURITY")
    print("=" * 80)
    
    # =========================================================================
    # PASO 1: CREAR/ACTUALIZAR DEPARTAMENTOS
    # =========================================================================
    
    departments_data = [
        {
            'code': 'RRHH',
            'name': 'Recursos Humanos',
            'type': 'RRHH',
            'description': 'Gestión del talento humano, reclutamiento, capacitación y bienestar del personal.'
        },
        {
            'code': 'SIST',
            'name': 'Sistemas y Tecnología',
            'type': 'SISTEMAS',
            'description': 'Desarrollo de software, infraestructura tecnológica y soporte técnico.'
        },
        {
            'code': 'MKT',
            'name': 'Marketing y Comunicaciones',
            'type': 'MARKETING',  # NUEVO
            'description': 'Gestión de redes sociales, contenido digital, campañas publicitarias y comunicación corporativa.'
        },
        {
            'code': 'DGTL',
            'name': 'Transformación Digital',
            'type': 'DIGITAL',  # NUEVO
            'description': 'Marketing digital, desarrollo web, sistemas internos y automatización de procesos.'
        },
        {
            'code': 'OPS',
            'name': 'Operaciones',
            'type': 'OPERACIONES',
            'description': 'Coordinación y ejecución de servicios de seguridad física y vigilancia.'
        },
        {
            'code': 'SEG',
            'name': 'Seguridad Física',
            'type': 'SEGURIDAD',
            'description': 'Guardias, vigilantes y personal de seguridad en campo.'
        },
        {
            'code': 'ADM',
            'name': 'Administración',
            'type': 'ADMINISTRACION',
            'description': 'Gestión administrativa, documentación y trámites corporativos.'
        },
        {
            'code': 'FIN',
            'name': 'Finanzas y Contabilidad',
            'type': 'FINANZAS',
            'description': 'Contabilidad, presupuestos, nómina y gestión financiera.'
        },
        {
            'code': 'LOG',
            'name': 'Logística y Compras',
            'type': 'LOGISTICA',
            'description': 'Adquisiciones, inventarios y gestión de proveedores.'
        },
        {
            'code': 'MNT',
            'name': 'Mantenimiento',
            'type': 'MANTENIMIENTO',
            'description': 'Mantenimiento de instalaciones, equipos y vehículos.'
        },
        {
            'code': 'COM',
            'name': 'Comercial y Ventas',
            'type': 'COMERCIAL',  # NUEVO
            'description': 'Ventas, atención al cliente y desarrollo de nuevos negocios.'
        },
    ]
    
    print("\n📂 PASO 1: Creando/Actualizando Departamentos...")
    print("-" * 80)
    
    created_departments = {}
    for dept_data in departments_data:
        dept, created = Department.objects.update_or_create(
            code=dept_data['code'],
            defaults={
                'name': dept_data['name'],
                'department_type': dept_data['type'],
                'description': dept_data['description'],
                'is_active': True
            }
        )
        created_departments[dept_data['code']] = dept
        status = "✅ Creado" if created else "🔄 Actualizado"
        print(f"{status}: {dept.code} - {dept.name}")
    
    # =========================================================================
    # PASO 2: CREAR/ACTUALIZAR PUESTOS DE TRABAJO
    # =========================================================================
    
    positions_data = [
        # RECURSOS HUMANOS
        {
            'dept': 'RRHH',
            'code': 'RRHH-DIR',
            'title': 'Director de Recursos Humanos',
            'level': 'DIRECTIVO',
            'description': 'Lidera la estrategia de gestión del talento humano.',
            'salary_min': 2500.00,
            'salary_max': 4000.00
        },
        {
            'dept': 'RRHH',
            'code': 'RRHH-COOR',
            'title': 'Coordinador de RRHH',
            'level': 'COORDINACION',
            'description': 'Coordina procesos de reclutamiento y gestión del personal.',
            'salary_min': 1500.00,
            'salary_max': 2200.00
        },
        {
            'dept': 'RRHH',
            'code': 'RRHH-ESP',
            'title': 'Especialista en Reclutamiento',
            'level': 'OPERATIVO',
            'description': 'Reclutamiento, selección y onboarding de personal.',
            'salary_min': 800.00,
            'salary_max': 1200.00
        },
        {
            'dept': 'RRHH',
            'code': 'RRHH-CAP',
            'title': 'Especialista en Capacitación',
            'level': 'OPERATIVO',
            'description': 'Diseña e imparte programas de capacitación.',
            'salary_min': 800.00,
            'salary_max': 1200.00
        },
        
        # SISTEMAS Y TECNOLOGÍA
        {
            'dept': 'SIST',
            'code': 'SIST-DIR',
            'title': 'Director de Tecnología (CTO)',
            'level': 'DIRECTIVO',
            'description': 'Lidera la estrategia tecnológica de la empresa.',
            'salary_min': 3000.00,
            'salary_max': 5000.00
        },
        {
            'dept': 'SIST',
            'code': 'SIST-DEV',
            'title': 'Desarrollador Full Stack',
            'level': 'COORDINACION',
            'description': 'Desarrollo de aplicaciones web y sistemas internos.',
            'salary_min': 1500.00,
            'salary_max': 2500.00
        },
        {
            'dept': 'SIST',
            'code': 'SIST-SOP',
            'title': 'Técnico de Soporte',
            'level': 'OPERATIVO',
            'description': 'Soporte técnico y mantenimiento de equipos.',
            'salary_min': 600.00,
            'salary_max': 900.00
        },
        {
            'dept': 'SIST',
            'code': 'SIST-INF',
            'title': 'Administrador de Infraestructura',
            'level': 'COORDINACION',
            'description': 'Gestión de servidores, redes y seguridad informática.',
            'salary_min': 1200.00,
            'salary_max': 1800.00
        },
        
        # TRANSFORMACIÓN DIGITAL (TU DEPARTAMENTO)
        {
            'dept': 'DGTL',
            'code': 'DGTL-MGR',
            'title': 'Especialista en Marketing Digital y Desarrollo',
            'level': 'COORDINACION',
            'description': 'Gestión de redes sociales, creación de contenido, desarrollo web, configuración de sistemas y automatización de procesos digitales.',
            'salary_min': 1800.00,
            'salary_max': 2800.00,
            'responsibilities': [
                'Administrar y gestionar redes sociales corporativas',
                'Responder y gestionar la comunidad online',
                'Crear contenido digital (textos, imágenes, videos)',
                'Medir resultados y analítica digital',
                'Planificar y ejecutar campañas publicitarias',
                'Configurar y desarrollar páginas web y aplicaciones',
                'Atender solicitudes de sistemas y programación',
                'Implementar automatizaciones y mejoras tecnológicas',
                'Diseñar estrategias de transformación digital'
            ]
        },
        {
            'dept': 'DGTL',
            'code': 'DGTL-CM',
            'title': 'Community Manager',
            'level': 'OPERATIVO',
            'description': 'Gestión de comunidades online y atención al cliente digital.',
            'salary_min': 600.00,
            'salary_max': 1000.00
        },
        {
            'dept': 'DGTL',
            'code': 'DGTL-DIS',
            'title': 'Diseñador Gráfico Digital',
            'level': 'OPERATIVO',
            'description': 'Creación de contenido visual para redes y web.',
            'salary_min': 700.00,
            'salary_max': 1200.00
        },
        
        # MARKETING Y COMUNICACIONES
        {
            'dept': 'MKT',
            'code': 'MKT-DIR',
            'title': 'Director de Marketing',
            'level': 'DIRECTIVO',
            'description': 'Lidera la estrategia de marketing y comunicación.',
            'salary_min': 2000.00,
            'salary_max': 3500.00
        },
        {
            'dept': 'MKT',
            'code': 'MKT-ESP',
            'title': 'Especialista en Marketing',
            'level': 'COORDINACION',
            'description': 'Ejecuta estrategias de marketing y publicidad.',
            'salary_min': 1000.00,
            'salary_max': 1500.00
        },
        
        # OPERACIONES
        {
            'dept': 'OPS',
            'code': 'OPS-DIR',
            'title': 'Director de Operaciones',
            'level': 'DIRECTIVO',
            'description': 'Lidera las operaciones de seguridad y servicios.',
            'salary_min': 2500.00,
            'salary_max': 4000.00
        },
        {
            'dept': 'OPS',
            'code': 'OPS-COOR',
            'title': 'Coordinador de Operaciones',
            'level': 'COORDINACION',
            'description': 'Coordina servicios y personal operativo.',
            'salary_min': 1200.00,
            'salary_max': 1800.00
        },
        {
            'dept': 'OPS',
            'code': 'OPS-SUP',
            'title': 'Supervisor de Campo',
            'level': 'SUPERVISION',
            'description': 'Supervisa personal de seguridad en campo.',
            'salary_min': 700.00,
            'salary_max': 1000.00
        },
        
        # SEGURIDAD FÍSICA
        {
            'dept': 'SEG',
            'code': 'SEG-JEFE',
            'title': 'Jefe de Seguridad',
            'level': 'COORDINACION',
            'description': 'Coordina equipos de guardias y vigilantes.',
            'salary_min': 800.00,
            'salary_max': 1200.00
        },
        {
            'dept': 'SEG',
            'code': 'SEG-GUARD',
            'title': 'Guardia de Seguridad',
            'level': 'OPERATIVO',
            'description': 'Vigilancia y seguridad física de instalaciones.',
            'salary_min': 460.00,
            'salary_max': 600.00
        },
        {
            'dept': 'SEG',
            'code': 'SEG-VIG',
            'title': 'Vigilante',
            'level': 'OPERATIVO',
            'description': 'Control de acceso y rondas de seguridad.',
            'salary_min': 460.00,
            'salary_max': 550.00
        },
        
        # ADMINISTRACIÓN
        {
            'dept': 'ADM',
            'code': 'ADM-DIR',
            'title': 'Director Administrativo',
            'level': 'DIRECTIVO',
            'description': 'Lidera la gestión administrativa de la empresa.',
            'salary_min': 2000.00,
            'salary_max': 3000.00
        },
        {
            'dept': 'ADM',
            'code': 'ADM-AST',
            'title': 'Asistente Administrativo',
            'level': 'OPERATIVO',
            'description': 'Apoyo en gestión documental y trámites.',
            'salary_min': 500.00,
            'salary_max': 700.00
        },
        {
            'dept': 'ADM',
            'code': 'ADM-REC',
            'title': 'Recepcionista',
            'level': 'OPERATIVO',
            'description': 'Atención al público y gestión de llamadas.',
            'salary_min': 460.00,
            'salary_max': 600.00
        },
        
        # FINANZAS
        {
            'dept': 'FIN',
            'code': 'FIN-DIR',
            'title': 'Director Financiero (CFO)',
            'level': 'DIRECTIVO',
            'description': 'Lidera la gestión financiera y contable.',
            'salary_min': 2500.00,
            'salary_max': 4000.00
        },
        {
            'dept': 'FIN',
            'code': 'FIN-CONT',
            'title': 'Contador',
            'level': 'COORDINACION',
            'description': 'Contabilidad general y estados financieros.',
            'salary_min': 1000.00,
            'salary_max': 1500.00
        },
        {
            'dept': 'FIN',
            'code': 'FIN-NOM',
            'title': 'Analista de Nómina',
            'level': 'OPERATIVO',
            'description': 'Procesamiento de nómina y beneficios.',
            'salary_min': 700.00,
            'salary_max': 1000.00
        },
        
        # LOGÍSTICA
        {
            'dept': 'LOG',
            'code': 'LOG-COOR',
            'title': 'Coordinador de Logística',
            'level': 'COORDINACION',
            'description': 'Coordina compras e inventarios.',
            'salary_min': 1000.00,
            'salary_max': 1500.00
        },
        {
            'dept': 'LOG',
            'code': 'LOG-COMP',
            'title': 'Auxiliar de Compras',
            'level': 'OPERATIVO',
            'description': 'Gestión de pedidos y proveedores.',
            'salary_min': 550.00,
            'salary_max': 800.00
        },
        {
            'dept': 'LOG',
            'code': 'LOG-ALM',
            'title': 'Almacenista',
            'level': 'OPERATIVO',
            'description': 'Control de inventarios y bodega.',
            'salary_min': 460.00,
            'salary_max': 600.00
        },
        
        # MANTENIMIENTO
        {
            'dept': 'MNT',
            'code': 'MNT-JEFE',
            'title': 'Jefe de Mantenimiento',
            'level': 'COORDINACION',
            'description': 'Coordina mantenimiento de instalaciones.',
            'salary_min': 800.00,
            'salary_max': 1200.00
        },
        {
            'dept': 'MNT',
            'code': 'MNT-TEC',
            'title': 'Técnico de Mantenimiento',
            'level': 'OPERATIVO',
            'description': 'Reparación y mantenimiento general.',
            'salary_min': 550.00,
            'salary_max': 800.00
        },
        
        # COMERCIAL
        {
            'dept': 'COM',
            'code': 'COM-DIR',
            'title': 'Director Comercial',
            'level': 'DIRECTIVO',
            'description': 'Lidera estrategia de ventas y desarrollo comercial.',
            'salary_min': 2000.00,
            'salary_max': 3500.00
        },
        {
            'dept': 'COM',
            'code': 'COM-EJEC',
            'title': 'Ejecutivo de Ventas',
            'level': 'COORDINACION',
            'description': 'Ventas de servicios de seguridad.',
            'salary_min': 800.00,
            'salary_max': 2000.00
        },
        {
            'dept': 'COM',
            'code': 'COM-SAC',
            'title': 'Servicio al Cliente',
            'level': 'OPERATIVO',
            'description': 'Atención y soporte a clientes.',
            'salary_min': 550.00,
            'salary_max': 800.00
        },
    ]
    
    print("\n💼 PASO 2: Creando/Actualizando Puestos de Trabajo...")
    print("-" * 80)
    
    # Primero, desactivar todos los puestos antiguos para luego reactivar los válidos
    Position.objects.all().update(is_active=False)
    print("⏸️  Puestos existentes marcados como inactivos temporalmente...")
    
    created_positions = {}
    for pos_data in positions_data:
        dept = created_departments.get(pos_data['dept'])
        if not dept:
            print(f"⚠️  Departamento {pos_data['dept']} no encontrado, saltando...")
            continue
        
        pos, created = Position.objects.update_or_create(
            code=pos_data['code'],
            defaults={
                'title': pos_data['title'],
                'department': dept,
                'level': pos_data['level'],
                'description': pos_data['description'],
                'min_salary': pos_data['salary_min'],
                'max_salary': pos_data['salary_max'],
                'is_active': True
            }
        )
        created_positions[pos_data['code']] = pos
        status = "✅ Creado" if created else "🔄 Actualizado"
        print(f"{status}: {pos.code} - {pos.title} ({dept.name})")
    
    # =========================================================================
    # PASO 3: RESUMEN Y ESTADÍSTICAS
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE REORGANIZACIÓN")
    print("=" * 80)
    
    print(f"\n🏢 Departamentos totales: {Department.objects.filter(is_active=True).count()}")
    print(f"💼 Puestos totales: {Position.objects.filter(is_active=True).count()}")
    
    print("\n📋 Distribución por Departamento:")
    print("-" * 80)
    for dept in Department.objects.filter(is_active=True).order_by('code'):
        positions_count = Position.objects.filter(department=dept, is_active=True).count()
        print(f"  {dept.code:6} - {dept.name:35} | {positions_count:2} puestos")
    
    print("\n" + "=" * 80)
    print("✅ REORGANIZACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    
    print("\n🎯 TU PUESTO CREADO:")
    print("-" * 80)
    your_position = Position.objects.get(code='DGTL-MGR')
    print(f"Código: {your_position.code}")
    print(f"Título: {your_position.title}")
    print(f"Departamento: {your_position.department.name}")
    print(f"Nivel: {your_position.get_level_display()}")
    print(f"Salario: ${your_position.min_salary:.2f} - ${your_position.max_salary:.2f}")
    print(f"\nDescripción:")
    print(f"  {your_position.description}")
    
    print("\n💡 RESPONSABILIDADES:")
    responsibilities = [
        'Administrar y gestionar redes sociales corporativas',
        'Responder y gestionar la comunidad online',
        'Crear contenido digital (textos, imágenes, videos)',
        'Medir resultados y analítica digital',
        'Planificar y ejecutar campañas publicitarias',
        'Configurar y desarrollar páginas web y aplicaciones',
        'Atender solicitudes de sistemas y programación',
        'Implementar automatizaciones y mejoras tecnológicas',
        'Diseñar estrategias de transformación digital'
    ]
    for i, resp in enumerate(responsibilities, 1):
        print(f"  {i}. {resp}")

if __name__ == '__main__':
    reorganize_departments_and_positions()
