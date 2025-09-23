#!/usr/bin/env python
"""
Crear solo los puestos de trabajo para EURO SECURITY
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
django.setup()

from departments.models import Department
from positions.models import Position

def create_positions():
    print("💼 CREANDO PUESTOS DE TRABAJO PARA EURO SECURITY")
    print("=" * 60)
    
    # Verificar que existen los departamentos
    departments = {}
    for dept in Department.objects.all():
        departments[dept.name] = dept
        print(f"📋 Departamento disponible: {dept.name} ({dept.code})")
    
    if not departments:
        print("❌ Error: No hay departamentos creados. Ejecuta primero create_departments_positions.py")
        return
    
    print(f"\n💼 CREANDO PUESTOS DE TRABAJO:")
    print("-" * 40)
    
    # PUESTOS POR DEPARTAMENTO
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
    
    positions_created = 0
    positions_existed = 0
    
    for pos_data in positions_data:
        dept_name = pos_data['department']
        
        if dept_name not in departments:
            print(f"❌ Departamento '{dept_name}' no encontrado")
            continue
            
        dept = departments[dept_name]
        
        position, created = Position.objects.get_or_create(
            name=pos_data['name'],
            department=dept,
            defaults={
                'description': pos_data['description'],
                'salary_min': pos_data['salary_min'],
                'salary_max': pos_data['salary_max'],
                'is_active': True
            }
        )
        
        if created:
            positions_created += 1
            status = "✅ Creado"
        else:
            positions_existed += 1
            status = "📋 Ya existe"
        
        print(f"{status} - {dept.name} → {position.name} (${pos_data['salary_min']}-${pos_data['salary_max']})")
    
    print(f"\n📊 RESUMEN:")
    print(f"   🏢 Departamentos: {Department.objects.count()}")
    print(f"   💼 Total puestos: {Position.objects.count()}")
    print(f"   ✅ Nuevos puestos creados: {positions_created}")
    print(f"   📋 Puestos que ya existían: {positions_existed}")
    
    print(f"\n🎯 ESTRUCTURA POR DEPARTAMENTO:")
    for dept in Department.objects.all():
        positions_count = dept.positions.count()
        print(f"   🏢 {dept.name} ({dept.code}): {positions_count} puestos")
    
    print(f"\n🎉 ¡PUESTOS DE TRABAJO CREADOS EXITOSAMENTE!")

if __name__ == '__main__':
    create_positions()
