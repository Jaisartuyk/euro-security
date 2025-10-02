from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forms.models import FormCategory, FormDocument


class Command(BaseCommand):
    help = 'Crear categorías y formularios de ejemplo para el sistema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creando sistema de formularios de ejemplo...'))
        
        # Obtener usuario admin para asignar como creador
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('❌ No se encontró usuario administrador'))
            return
        
        # Crear categorías
        categories_data = [
            {
                'name': 'Recursos Humanos',
                'description': 'Formularios relacionados con gestión de personal, contratación y beneficios',
                'icon': 'fas fa-users',
                'color': 'primary',
                'order': 1
            },
            {
                'name': 'Seguridad y Vigilancia',
                'description': 'Formularios específicos para operaciones de seguridad y reportes de incidentes',
                'icon': 'fas fa-shield-alt',
                'color': 'danger',
                'order': 2
            },
            {
                'name': 'Administración',
                'description': 'Formularios administrativos, solicitudes y documentos corporativos',
                'icon': 'fas fa-briefcase',
                'color': 'success',
                'order': 3
            },
            {
                'name': 'Médico y Salud',
                'description': 'Formularios médicos, certificados de salud y permisos por enfermedad',
                'icon': 'fas fa-heartbeat',
                'color': 'info',
                'order': 4
            },
            {
                'name': 'Legal y Compliance',
                'description': 'Documentos legales, contratos y formularios de cumplimiento',
                'icon': 'fas fa-gavel',
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
        
        # Crear formularios de ejemplo
        forms_data = [
            # Recursos Humanos
            {
                'title': 'Solicitud de Empleo',
                'description': 'Formulario estándar para solicitar empleo en Euro Security. Incluye información personal, experiencia laboral y referencias.',
                'category': 'Recursos Humanos',
                'required_permission': 'hr',
                'version': '2.1',
                'is_fillable': True
            },
            {
                'title': 'Evaluación de Desempeño',
                'description': 'Formulario para evaluación anual de desempeño de empleados. Incluye métricas de productividad y competencias.',
                'category': 'Recursos Humanos',
                'required_permission': 'management',
                'version': '1.5',
                'is_fillable': True
            },
            {
                'title': 'Solicitud de Vacaciones',
                'description': 'Formulario para solicitar días de vacaciones. Debe ser aprobado por el supervisor directo.',
                'category': 'Recursos Humanos',
                'required_permission': 'all',
                'version': '1.0',
                'is_fillable': True
            },
            
            # Seguridad y Vigilancia
            {
                'title': 'Reporte de Incidente de Seguridad',
                'description': 'Formulario para reportar incidentes de seguridad, robos, accidentes o situaciones irregulares.',
                'category': 'Seguridad y Vigilancia',
                'required_permission': 'supervisor',
                'version': '3.0',
                'is_fillable': True
            },
            {
                'title': 'Lista de Verificación de Rondas',
                'description': 'Checklist para verificar puntos de control durante las rondas de seguridad.',
                'category': 'Seguridad y Vigilancia',
                'required_permission': 'all',
                'version': '2.2',
                'is_fillable': True
            },
            {
                'title': 'Protocolo de Emergencia',
                'description': 'Procedimientos detallados para manejo de emergencias y evacuaciones.',
                'category': 'Seguridad y Vigilancia',
                'required_permission': 'all',
                'version': '1.8',
                'is_fillable': False
            },
            
            # Administración
            {
                'title': 'Solicitud de Materiales y Suministros',
                'description': 'Formulario para solicitar materiales, uniformes, equipos y suministros de trabajo.',
                'category': 'Administración',
                'required_permission': 'supervisor',
                'version': '1.3',
                'is_fillable': True
            },
            {
                'title': 'Reporte de Gastos',
                'description': 'Formulario para reportar gastos de trabajo, viáticos y reembolsos.',
                'category': 'Administración',
                'required_permission': 'management',
                'version': '2.0',
                'is_fillable': True
            },
            
            # Médico y Salud
            {
                'title': 'Certificado Médico',
                'description': 'Formato estándar para certificados médicos y permisos por enfermedad.',
                'category': 'Médico y Salud',
                'required_permission': 'hr',
                'version': '1.0',
                'is_fillable': True
            },
            {
                'title': 'Examen Médico Ocupacional',
                'description': 'Formulario para exámenes médicos de ingreso, periódicos y de retiro.',
                'category': 'Médico y Salud',
                'required_permission': 'hr',
                'version': '1.4',
                'is_fillable': True
            },
            
            # Legal y Compliance
            {
                'title': 'Contrato de Confidencialidad',
                'description': 'Acuerdo de confidencialidad para empleados con acceso a información sensible.',
                'category': 'Legal y Compliance',
                'required_permission': 'hr',
                'version': '2.1',
                'is_fillable': False
            },
            {
                'title': 'Política de Seguridad de la Información',
                'description': 'Documento con políticas y procedimientos de seguridad informática.',
                'category': 'Legal y Compliance',
                'required_permission': 'all',
                'version': '1.0',
                'is_fillable': False
            }
        ]
        
        # Mapear categorías por nombre
        category_map = {cat.name: cat for cat in created_categories}
        
        for form_data in forms_data:
            category = category_map[form_data['category']]
            
            # Crear el formulario (sin archivo por ahora)
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
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 ¡Sistema de formularios creado exitosamente!'))
        self.stdout.write(f'📁 Categorías: {total_categories}')
        self.stdout.write(f'📄 Formularios: {total_forms}')
        self.stdout.write(f'\n🔗 Accede al sistema en: /formularios/')
        self.stdout.write(f'⚙️  Gestiona desde admin: /admin/forms/')
        
        self.stdout.write(self.style.WARNING('\n📝 NOTA: Los formularios se crearon sin archivos.'))
        self.stdout.write('   Sube los archivos PDF desde el admin de Django.')
