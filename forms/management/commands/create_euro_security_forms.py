from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forms.models import FormCategory, FormDocument


class Command(BaseCommand):
    help = 'Crear sistema de formularios personalizado para Euro Security'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creando sistema de formularios Euro Security...'))
        
        # Obtener usuario admin para asignar como creador
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('❌ No se encontró usuario administrador'))
            return
        
        # Crear categorías específicas para Euro Security
        categories_data = [
            {
                'name': 'Recursos Humanos',
                'description': 'Formularios de selección, contratación y gestión de personal',
                'icon': 'fas fa-users',
                'color': 'primary',
                'order': 1
            },
            {
                'name': 'Operaciones de Seguridad',
                'description': 'Formularios operativos para servicios de seguridad y vigilancia',
                'icon': 'fas fa-shield-alt',
                'color': 'danger',
                'order': 2
            },
            {
                'name': 'Administración Corporativa',
                'description': 'Formularios administrativos y de gestión empresarial',
                'icon': 'fas fa-building',
                'color': 'success',
                'order': 3
            },
            {
                'name': 'Salud y Seguridad Laboral',
                'description': 'Formularios médicos y de seguridad ocupacional',
                'icon': 'fas fa-heartbeat',
                'color': 'info',
                'order': 4
            },
            {
                'name': 'Legal y Compliance',
                'description': 'Documentos legales y de cumplimiento normativo',
                'icon': 'fas fa-balance-scale',
                'color': 'warning',
                'order': 5
            }
        ]
        
        created_categories = []
        for cat_data in categories_data:
            category, created = FormCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'✅ Categoría creada: {category.name}')
            else:
                self.stdout.write(f'ℹ️  Categoría existente: {category.name}')
            created_categories.append(category)
        
        # Crear formularios específicos de Euro Security
        forms_data = [
            # Recursos Humanos
            {
                'title': 'Formulario de Entrevista Laboral',
                'description': 'Formulario estructurado para evaluación de candidatos en procesos de selección. Incluye evaluación de presentación, formación académica, experiencia laboral, habilidades y competencias. Código: OP-EUEC-01',
                'category': 'Recursos Humanos',
                'required_permission': 'hr',
                'version': '1.0',
                'is_fillable': True,
                'code': 'OP-EUEC-01'
            },
            {
                'title': 'Solicitud de Empleo Euro Security',
                'description': 'Formulario oficial para postulación a puestos de trabajo en Euro Security. Incluye datos personales, experiencia laboral, referencias y documentación requerida.',
                'category': 'Recursos Humanos',
                'required_permission': 'hr',
                'version': '2.0',
                'is_fillable': True,
                'code': 'OP-EUEC-02'
            },
            {
                'title': 'Evaluación de Desempeño Anual',
                'description': 'Formulario para evaluación periódica del desempeño de empleados. Incluye métricas de productividad, competencias técnicas y desarrollo profesional.',
                'category': 'Recursos Humanos',
                'required_permission': 'management',
                'version': '1.5',
                'is_fillable': True,
                'code': 'OP-EUEC-03'
            },
            
            # Operaciones de Seguridad
            {
                'title': 'Reporte de Incidente de Seguridad',
                'description': 'Formulario para documentar incidentes de seguridad, robos, accidentes o situaciones irregulares durante el servicio de vigilancia.',
                'category': 'Operaciones de Seguridad',
                'required_permission': 'supervisor',
                'version': '3.0',
                'is_fillable': True,
                'code': 'OP-EUSEG-01'
            },
            {
                'title': 'Lista de Verificación de Rondas',
                'description': 'Checklist para verificar puntos de control durante las rondas de seguridad. Incluye horarios, observaciones y firmas de responsables.',
                'category': 'Operaciones de Seguridad',
                'required_permission': 'all',
                'version': '2.2',
                'is_fillable': True,
                'code': 'OP-EUSEG-02'
            },
            {
                'title': 'Protocolo de Emergencia',
                'description': 'Procedimientos detallados para manejo de emergencias, evacuaciones y situaciones críticas en instalaciones bajo custodia.',
                'category': 'Operaciones de Seguridad',
                'required_permission': 'all',
                'version': '1.8',
                'is_fillable': False,
                'code': 'OP-EUSEG-03'
            },
            
            # Administración Corporativa
            {
                'title': 'Solicitud de Materiales y Equipos',
                'description': 'Formulario para solicitar materiales, uniformes, equipos de seguridad y suministros necesarios para las operaciones.',
                'category': 'Administración Corporativa',
                'required_permission': 'supervisor',
                'version': '1.3',
                'is_fillable': True,
                'code': 'OP-EUADM-01'
            },
            {
                'title': 'Reporte de Gastos Operativos',
                'description': 'Formulario para reportar gastos operativos, viáticos, combustible y otros gastos relacionados con el servicio.',
                'category': 'Administración Corporativa',
                'required_permission': 'management',
                'version': '2.0',
                'is_fillable': True,
                'code': 'OP-EUADM-02'
            },
            
            # Salud y Seguridad Laboral
            {
                'title': 'Certificado Médico Ocupacional',
                'description': 'Formato para certificados médicos ocupacionales, exámenes de ingreso, periódicos y de retiro según normativas laborales.',
                'category': 'Salud y Seguridad Laboral',
                'required_permission': 'hr',
                'version': '1.0',
                'is_fillable': True,
                'code': 'OP-EUMED-01'
            },
            {
                'title': 'Reporte de Accidente Laboral',
                'description': 'Formulario para reportar accidentes laborales, lesiones o incidentes relacionados con la seguridad ocupacional.',
                'category': 'Salud y Seguridad Laboral',
                'required_permission': 'supervisor',
                'version': '1.4',
                'is_fillable': True,
                'code': 'OP-EUMED-02'
            },
            
            # Legal y Compliance
            {
                'title': 'Acuerdo de Confidencialidad',
                'description': 'Contrato de confidencialidad para empleados con acceso a información sensible de clientes y operaciones de seguridad.',
                'category': 'Legal y Compliance',
                'required_permission': 'hr',
                'version': '2.1',
                'is_fillable': False,
                'code': 'OP-EULEG-01'
            },
            {
                'title': 'Política de Seguridad de la Información',
                'description': 'Documento con políticas y procedimientos de seguridad informática y manejo de datos confidenciales.',
                'category': 'Legal y Compliance',
                'required_permission': 'all',
                'version': '1.0',
                'is_fillable': False,
                'code': 'OP-EULEG-02'
            }
        ]
        
        # Mapear categorías por nombre
        category_map = {cat.name: cat for cat in created_categories}
        
        for form_data in forms_data:
            category = category_map[form_data['category']]
            
            # Crear el formulario
            form_doc, created = FormDocument.objects.get_or_create(
                title=form_data['title'],
                category=category,
                defaults={
                    'description': form_data['description'],
                    'required_permission': form_data['required_permission'],
                    'version': form_data['version'],
                    'is_fillable': form_data['is_fillable'],
                    'created_by': admin_user,
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f'✅ Formulario creado: {form_doc.title}')
            else:
                self.stdout.write(f'ℹ️  Formulario existente: {form_doc.title}')
        
        # Estadísticas finales
        total_categories = FormCategory.objects.count()
        total_forms = FormDocument.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 ¡Sistema Euro Security creado exitosamente!'))
        self.stdout.write(f'📁 Categorías: {total_categories}')
        self.stdout.write(f'📄 Formularios: {total_forms}')
        self.stdout.write(f'\n🔗 Accede al sistema en: /formularios/')
        self.stdout.write(f'⚙️  Gestiona desde admin: /admin/forms/')
        
        self.stdout.write(self.style.WARNING('\n📝 PRÓXIMOS PASOS:'))
        self.stdout.write('1. Sube los archivos PDF desde el admin Django')
        self.stdout.write('2. Agrega letterhead.jpg como encabezado')
        self.stdout.write('3. Configura permisos específicos si es necesario')
        self.stdout.write('4. Prueba las descargas desde /formularios/')
