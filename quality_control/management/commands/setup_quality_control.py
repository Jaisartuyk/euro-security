"""
Comando para inicializar el Sistema de Control de Calidad con datos de ejemplo
"""
from django.core.management.base import BaseCommand
from quality_control.models import RiskCategory, Risk, ControlMeasure


class Command(BaseCommand):
    help = 'Inicializa el Sistema de Control de Calidad con categorías y datos de ejemplo'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando configuración del Sistema de Control de Calidad...'))
        
        # Crear categorías
        self.create_categories()
        
        # Crear riesgos de ejemplo
        self.create_sample_risks()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sistema de Control de Calidad configurado exitosamente!'))
        self.stdout.write(self.style.SUCCESS('📊 Accede a /admin/ para gestionar riesgos'))

    def create_categories(self):
        """Crear las 5 categorías principales de riesgos"""
        self.stdout.write('\n📋 Creando categorías de riesgos...')
        
        categories = [
            {
                'name': 'Riesgos Operativos',
                'category_type': 'OPERATIVO',
                'description': 'Errores en procedimientos de control de acceso, fallas en sistemas de vigilancia, '
                              'deficiencia en planes de contingencia, equipos de seguridad no actualizados, '
                              'incumplimientos de normas legales y regulatorias.',
                'color': '#007bff',
                'icon': 'fa-cogs'
            },
            {
                'name': 'Riesgos Tecnológicos',
                'category_type': 'TECNOLOGICO',
                'description': 'Fallas en sistemas de CCTV y cámaras, problemas en sistemas de alarmas, '
                              'obsolescencia de datos de clientes, falta de actualización tecnológica, '
                              'insuficiencia de equipos técnicos.',
                'color': '#6f42c1',
                'icon': 'fa-laptop-code'
            },
            {
                'name': 'Riesgos de Capital Humano',
                'category_type': 'CAPITAL_HUMANO',
                'description': 'Falta de capacitación del personal, manejo de crisis inadecuado, '
                              'alta rotación de personal, fatiga laboral, conductas inadecuadas, '
                              'accidentes laborales, carencias cognitivas del personal.',
                'color': '#fd7e14',
                'icon': 'fa-users'
            },
            {
                'name': 'Riesgos del Entorno y Externos',
                'category_type': 'ENTORNO',
                'description': 'Amenazas delictivas externas, robos, asaltos, vandalismo, '
                              'conflictos sociales en zonas de servicio, desastres naturales, '
                              'competencia desleal.',
                'color': '#28a745',
                'icon': 'fa-globe'
            },
            {
                'name': 'Riesgos Reputacionales',
                'category_type': 'REPUTACIONAL',
                'description': 'Mala atención al cliente, incumplimiento de contratos, '
                              'incidentes públicos con sumarias de seguridad, pérdida de confianza del cliente, '
                              'fallas en la protección.',
                'color': '#dc3545',
                'icon': 'fa-exclamation-triangle'
            },
        ]
        
        for cat_data in categories:
            category, created = RiskCategory.objects.get_or_create(
                category_type=cat_data['category_type'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'  ✓ Creada: {category.name}')
            else:
                self.stdout.write(f'  ⏭️  Ya existe: {category.name}')

    def create_sample_risks(self):
        """Crear riesgos de ejemplo basados en las imágenes proporcionadas"""
        self.stdout.write('\n📊 Creando riesgos de ejemplo...')
        
        # Obtener categorías
        operativo = RiskCategory.objects.get(category_type='OPERATIVO')
        tecnologico = RiskCategory.objects.get(category_type='TECNOLOGICO')
        capital_humano = RiskCategory.objects.get(category_type='CAPITAL_HUMANO')
        reputacional = RiskCategory.objects.get(category_type='REPUTACIONAL')
        
        risks = [
            {
                'code': 'RSG-001',
                'title': 'Incumplimiento de protocolos por el personal',
                'description': 'El personal de seguridad no sigue los protocolos establecidos de control de acceso, '
                              'lo que puede resultar en brechas de seguridad.',
                'category': operativo,
                'probability': 4,
                'impact': 4,
            },
            {
                'code': 'RSG-002',
                'title': 'Fallo en cámaras de vigilancia',
                'description': 'Las cámaras de vigilancia presentan fallas técnicas o no están operativas, '
                              'dejando áreas sin monitoreo.',
                'category': tecnologico,
                'probability': 3,
                'impact': 4,
            },
            {
                'code': 'RSG-003',
                'title': 'Rotación alta de guardias',
                'description': 'Alta rotación del personal de seguridad que afecta la continuidad del servicio '
                              'y aumenta los errores.',
                'category': capital_humano,
                'probability': 4,
                'impact': 3,
            },
            {
                'code': 'RSG-004',
                'title': 'Incumplimiento de normativas de seguridad',
                'description': 'No cumplimiento de normas informativas de seguridad que puede resultar en '
                              'sanciones legales.',
                'category': operativo,
                'probability': 2,
                'impact': 5,
            },
            {
                'code': 'RSG-005',
                'title': 'Quejas frecuentes de clientes',
                'description': 'Clientes insatisfechos con el servicio presentan quejas frecuentes que afectan '
                              'la reputación de la empresa.',
                'category': reputacional,
                'probability': 3,
                'impact': 4,
            },
        ]
        
        for risk_data in risks:
            risk, created = Risk.objects.get_or_create(
                code=risk_data['code'],
                defaults=risk_data
            )
            if created:
                self.stdout.write(f'  ✓ Creado: [{risk.code}] {risk.title} - Nivel: {risk.get_risk_level_display()}')
                
                # Crear medida de control de ejemplo
                ControlMeasure.objects.create(
                    risk=risk,
                    title=f'Capacitación constante, supervisión de turnos',
                    description=f'Implementar programa de capacitación continua y supervisión activa para mitigar el riesgo.',
                    priority='ALTA',
                    status='EN_PROGRESO'
                )
                self.stdout.write(f'    → Medida de control creada')
            else:
                self.stdout.write(f'  ⏭️  Ya existe: [{risk.code}] {risk.title}')
