"""
Management command para crear formularios de visitantes y toma de conocimiento
"""
from django.core.management.base import BaseCommand
from forms.models import FormTemplate, FormField, FormCategory


class Command(BaseCommand):
    help = 'Crea formularios de visitantes y toma de conocimiento para Euro Security'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creando formularios de visitantes...'))
        
        # Obtener categorías
        try:
            security_category = FormCategory.objects.get(name='Operaciones de Seguridad')
        except FormCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Categoría no encontrada'))
            return
        
        # =====================================================================
        # FORMULARIO 1: REGISTRO DE VISITANTES URBANIZACIÓN
        # =====================================================================
        
        visitor_template, created = FormTemplate.objects.get_or_create(
            code='OPA-EUEC-12',
            defaults={
                'title': 'Registro de Visitantes Urbanización',
                'description': 'Control de ingreso y salida de visitantes en urbanizaciones',
                'category': security_category,
                'version': '1.0',
                'is_active': True,
                'requires_approval': False,
                'allow_draft': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Creado: {visitor_template.title}'))
            
            # Campos del formulario de visitantes
            visitor_fields = [
                # Columna 1: Fecha
                {
                    'name': 'fecha',
                    'label': 'Fecha',
                    'field_type': 'date',
                    'is_required': True,
                    'order': 1,
                    'section': 'Información del Registro',
                },
                # Columna 2: Nombres
                {
                    'name': 'nombres',
                    'label': 'Nombres',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 2,
                    'section': 'Información del Registro',
                    'max_length': 100,
                },
                # Columna 3: Apellidos
                {
                    'name': 'apellidos',
                    'label': 'Apellidos',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 3,
                    'section': 'Información del Registro',
                    'max_length': 100,
                },
                # Columna 4: RCI (Cédula)
                {
                    'name': 'rci',
                    'label': 'RCI / Cédula',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 4,
                    'section': 'Información del Registro',
                    'max_length': 20,
                    'help_text': 'Número de identificación del visitante',
                },
                # Columna 5: M/Escolar (Matrícula/Escolar)
                {
                    'name': 'm_escolar',
                    'label': 'M/Escolar',
                    'field_type': 'text',
                    'is_required': False,
                    'order': 5,
                    'section': 'Información del Registro',
                    'max_length': 20,
                    'help_text': 'Matrícula o identificación escolar',
                },
                # Columna 6: Propietario
                {
                    'name': 'propietario',
                    'label': 'Propietario',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 6,
                    'section': 'Información del Registro',
                    'max_length': 100,
                    'help_text': 'Nombre del propietario que autoriza',
                },
                # Columna 7: N. Inmueble
                {
                    'name': 'n_inmueble',
                    'label': 'N. Inmueble',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 7,
                    'section': 'Información del Registro',
                    'max_length': 20,
                    'help_text': 'Número de casa/departamento',
                },
                # Columna 8: H. Salida
                {
                    'name': 'h_salida',
                    'label': 'H. Salida',
                    'field_type': 'text',
                    'is_required': False,
                    'order': 8,
                    'section': 'Información del Registro',
                    'max_length': 10,
                    'help_text': 'Hora de salida (HH:MM)',
                },
            ]
            
            for field_data in visitor_fields:
                FormField.objects.create(
                    template=visitor_template,
                    **field_data
                )
            
            self.stdout.write(self.style.SUCCESS(f'   ✓ {len(visitor_fields)} campos creados'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Ya existe: {visitor_template.title}'))
        
        # =====================================================================
        # FORMULARIO 2: REGISTRO TOMA DE CONOCIMIENTO
        # =====================================================================
        
        knowledge_template, created = FormTemplate.objects.get_or_create(
            code='OPA-EUEC-08',
            defaults={
                'title': 'Registro Toma de Conocimiento',
                'description': 'Registro de capacitaciones y toma de conocimiento del personal',
                'category': security_category,
                'version': '1.0',
                'is_active': True,
                'requires_approval': True,
                'allow_draft': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Creado: {knowledge_template.title}'))
            
            # Campos del formulario de toma de conocimiento
            knowledge_fields = [
                # Sección 1: Información General
                {
                    'name': 'area',
                    'label': 'Área',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 1,
                    'section': 'Información General',
                    'max_length': 100,
                    'help_text': 'Área o departamento',
                },
                {
                    'name': 'fecha',
                    'label': 'Fecha',
                    'field_type': 'date',
                    'is_required': True,
                    'order': 2,
                    'section': 'Información General',
                },
                {
                    'name': 'capacitador',
                    'label': 'Capacitador',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 3,
                    'section': 'Información General',
                    'max_length': 100,
                    'help_text': 'Nombre del capacitador',
                },
                {
                    'name': 'tema_tratado',
                    'label': 'Tema Tratado',
                    'field_type': 'textarea',
                    'is_required': True,
                    'order': 4,
                    'section': 'Información General',
                    'help_text': 'Descripción del tema de la capacitación',
                },
                
                # Sección 2: Datos del Personal (Tabla)
                {
                    'name': 'nombres',
                    'label': 'Nombres',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 5,
                    'section': 'Datos del Personal',
                    'max_length': 100,
                },
                {
                    'name': 'apellidos',
                    'label': 'Apellidos',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 6,
                    'section': 'Datos del Personal',
                    'max_length': 100,
                },
                {
                    'name': 'cedula',
                    'label': 'Cédula',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 7,
                    'section': 'Datos del Personal',
                    'max_length': 20,
                },
                {
                    'name': 'firma',
                    'label': 'Firma',
                    'field_type': 'signature',
                    'is_required': True,
                    'order': 8,
                    'section': 'Datos del Personal',
                    'help_text': 'Firma digital del participante',
                },
                {
                    'name': 'cargo',
                    'label': 'Cargo',
                    'field_type': 'text',
                    'is_required': True,
                    'order': 9,
                    'section': 'Datos del Personal',
                    'max_length': 100,
                },
            ]
            
            for field_data in knowledge_fields:
                FormField.objects.create(
                    template=knowledge_template,
                    **field_data
                )
            
            self.stdout.write(self.style.SUCCESS(f'   ✓ {len(knowledge_fields)} campos creados'))
        else:
            self.stdout.write(self.style.WARNING(f'⚠️  Ya existe: {knowledge_template.title}'))
        
        self.stdout.write(self.style.SUCCESS('\n✨ ¡Formularios de visitantes creados exitosamente!'))
        self.stdout.write(self.style.SUCCESS(f'📋 Total: 2 formularios'))
