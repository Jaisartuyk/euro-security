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
        """Crear riesgos reales basados en la matriz proporcionada"""
        self.stdout.write('\n📊 Creando riesgos identificados...')
        
        # Obtener categorías
        operativo = RiskCategory.objects.get(category_type='OPERATIVO')
        tecnologico = RiskCategory.objects.get(category_type='TECNOLOGICO')
        capital_humano = RiskCategory.objects.get(category_type='CAPITAL_HUMANO')
        entorno = RiskCategory.objects.get(category_type='ENTORNO')
        reputacional = RiskCategory.objects.get(category_type='REPUTACIONAL')
        
        risks = [
            # RIESGOS OPERATIVOS
            {
                'code': 'ROP-001',
                'title': 'Errores en los procedimientos de control de acceso',
                'description': 'Dejar pasar sin autorización. Errores en los procedimientos de control de acceso que pueden comprometer la seguridad.',
                'category': operativo,
                'probability': 4,
                'impact': 4,
            },
            {
                'code': 'ROP-002',
                'title': 'Fallas en la coordinación de rondas de seguridad',
                'description': 'Fallas en la coordinación de rondas de seguridad que dejan áreas desprotegidas.',
                'category': operativo,
                'probability': 3,
                'impact': 3,
            },
            {
                'code': 'ROP-003',
                'title': 'Comunicación ineficaz entre turnos o áreas',
                'description': 'Información incompleta de novedades. Comunicación ineficaz que genera falta de información crítica.',
                'category': operativo,
                'probability': 4,
                'impact': 3,
            },
            {
                'code': 'ROP-004',
                'title': 'Incumplimientos de normas legales y regulatorias',
                'description': 'Incumplimientos de normas legales y regulatorias que pueden resultar en sanciones.',
                'category': operativo,
                'probability': 2,
                'impact': 5,
            },
            {
                'code': 'ROP-005',
                'title': 'Errores en los procedimientos operativos',
                'description': 'Errores sistemáticos en los procedimientos operativos que afectan la calidad del servicio.',
                'category': operativo,
                'probability': 3,
                'impact': 3,
            },
            
            # RIESGOS TECNOLÓGICOS
            {
                'code': 'TEC-001',
                'title': 'Fallas en sistemas de CCTV',
                'description': 'Cámaras apagadas o con poca cobertura. Fallas en sistemas de CCTV que dejan áreas sin vigilancia.',
                'category': tecnologico,
                'probability': 3,
                'impact': 4,
            },
            {
                'code': 'TEC-002',
                'title': 'Problemas en sistemas de alarmas',
                'description': 'Fallas alarmas, falta de mantenimiento. Problemas que impiden la detección oportuna de incidentes.',
                'category': tecnologico,
                'probability': 3,
                'impact': 4,
            },
            {
                'code': 'TEC-003',
                'title': 'Obsolescencia de base de datos de clientes',
                'description': 'Obsolescencia de base de datos de clientes que afecta la gestión de información.',
                'category': tecnologico,
                'probability': 2,
                'impact': 3,
            },
            {
                'code': 'TEC-004',
                'title': 'Dependencia de tecnología no actualizada',
                'description': 'Dependencia de tecnología no actualizada o en desreparo que compromete operaciones.',
                'category': tecnologico,
                'probability': 3,
                'impact': 4,
            },
            {
                'code': 'TEC-005',
                'title': 'Fallas en sistemas de comunicación',
                'description': 'Radios. Fallas en sistemas de comunicación que impiden coordinación efectiva.',
                'category': tecnologico,
                'probability': 3,
                'impact': 3,
            },
            {
                'code': 'TEC-006',
                'title': 'Insuficiencia de equipos técnicos y tecnológicos',
                'description': 'Insuficiencia de equipos técnicos y tecnológicos para cubrir necesidades operativas.',
                'category': tecnologico,
                'probability': 3,
                'impact': 3,
            },
            
            # RIESGOS DE CAPITAL HUMANO
            {
                'code': 'CAP-001',
                'title': 'Falta de capacitación del personal de seguridad',
                'description': 'Manejo de crisis, primeros auxilios, protocolos. Falta de capacitación que afecta la respuesta ante emergencias.',
                'category': capital_humano,
                'probability': 4,
                'impact': 4,
            },
            {
                'code': 'CAP-002',
                'title': 'Alta rotación de personal',
                'description': 'Lo que afecta la continuidad del servicio. Alta rotación que genera pérdida de conocimiento y experiencia.',
                'category': capital_humano,
                'probability': 4,
                'impact': 3,
            },
            {
                'code': 'CAP-003',
                'title': 'Fatiga laboral y exceso de horas extras',
                'description': 'Que disminuye la atención y aumenta los errores. Fatiga que compromete el desempeño del personal.',
                'category': capital_humano,
                'probability': 4,
                'impact': 3,
            },
            {
                'code': 'CAP-004',
                'title': 'Conductas inadecuadas',
                'description': 'Corrupción, abuso de autoridad, incumplimiento de normas. Conductas que afectan la integridad del servicio.',
                'category': capital_humano,
                'probability': 2,
                'impact': 5,
            },
            {
                'code': 'CAP-005',
                'title': 'Accidentes laborales',
                'description': 'Lesiones, enfermedades laborales. Accidentes que afectan al personal y operaciones.',
                'category': capital_humano,
                'probability': 3,
                'impact': 4,
            },
            {
                'code': 'CAP-006',
                'title': 'Carencias cognitivas del personal',
                'description': 'Falta de conocimientos o habilidades necesarias para el desempeño efectivo.',
                'category': capital_humano,
                'probability': 3,
                'impact': 3,
            },
            
            # RIESGOS DEL ENTORNO Y EXTERNOS
            {
                'code': 'ENT-001',
                'title': 'Amenazas delictivas externas',
                'description': 'Robos, asaltos, vandalismo. Amenazas externas que ponen en riesgo instalaciones y personas.',
                'category': entorno,
                'probability': 3,
                'impact': 5,
            },
            {
                'code': 'ENT-002',
                'title': 'Conflictos sociales en zonas de servicio',
                'description': 'Manifestaciones, disturbios. Conflictos que afectan la operación normal del servicio.',
                'category': entorno,
                'probability': 2,
                'impact': 4,
            },
            {
                'code': 'ENT-003',
                'title': 'Clima o desastres naturales',
                'description': 'Inundaciones, terremotos. Desastres naturales que afectan la operación.',
                'category': entorno,
                'probability': 2,
                'impact': 4,
            },
            {
                'code': 'ENT-004',
                'title': 'Competencia desleal',
                'description': 'Empresas que ofrecen servicios a menor costo sin cumplir normativas. Competencia que afecta el mercado.',
                'category': entorno,
                'probability': 3,
                'impact': 3,
            },
            
            # RIESGOS REPUTACIONALES
            {
                'code': 'REP-001',
                'title': 'Mala atención al cliente o incumplimiento de contratos',
                'description': 'Mala atención que genera insatisfacción y pérdida de clientes.',
                'category': reputacional,
                'probability': 3,
                'impact': 4,
            },
            {
                'code': 'REP-002',
                'title': 'Incidentes públicos con guardias de seguridad',
                'description': 'Uso excesivo de fuerza, denuncias. Incidentes que dañan la imagen de la empresa.',
                'category': reputacional,
                'probability': 2,
                'impact': 5,
            },
            {
                'code': 'REP-003',
                'title': 'Pérdida de confianza del cliente por fallas en la protección',
                'description': 'Pérdida de confianza que afecta la retención y captación de clientes.',
                'category': reputacional,
                'probability': 3,
                'impact': 4,
            },
        ]
        
        created_count = 0
        for risk_data in risks:
            risk, created = Risk.objects.get_or_create(
                code=risk_data['code'],
                defaults=risk_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Creado: [{risk.code}] {risk.title} - Nivel: {risk.get_risk_level_display()}')
                
                # Crear medida de control de ejemplo
                ControlMeasure.objects.create(
                    risk=risk,
                    title=f'Medida de control para {risk.code}',
                    description=f'Implementar controles y procedimientos para mitigar el riesgo identificado.',
                    priority='ALTA' if risk.risk_level == 'ALTO' else 'MEDIA',
                    status='PENDIENTE'
                )
            else:
                self.stdout.write(f'  ⏭️  Ya existe: [{risk.code}] {risk.title}')
        
        self.stdout.write(f'\n✅ Total de riesgos creados: {created_count}')
