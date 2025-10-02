from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forms.models import FormCategory, FormTemplate, FormField


class Command(BaseCommand):
    help = 'Crear formularios dinámicos específicos de Euro Security'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creando formularios dinámicos Euro Security...'))
        
        # Obtener usuario admin
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('❌ No se encontró usuario administrador'))
            return
        
        # Obtener categorías
        try:
            rrhh_category = FormCategory.objects.get(name='Recursos Humanos')
            security_category = FormCategory.objects.get(name='Operaciones de Seguridad')
        except FormCategory.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Categorías no encontradas'))
            return
        
        # ============================================================================
        # 1. FORMULARIO DE HOJA DE VIDA (OP-EUEC-04)
        # ============================================================================
        
        hoja_vida_template, created = FormTemplate.objects.get_or_create(
            code='OP-EUEC-04',
            defaults={
                'title': 'Formulario de Hoja de Vida',
                'description': 'Formulario completo para registro de información personal, académica y laboral de candidatos.',
                'category': rrhh_category,
                'version': '1.0',
                'is_active': True,
                'requires_approval': True,
                'allow_draft': True,
                'required_permission': 'hr',
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write('✅ Plantilla Hoja de Vida creada')
            
            # Campos de datos personales
            FormField.objects.create(
                template=hoja_vida_template,
                name='foto',
                label='Fotografía',
                field_type='file',
                help_text='Suba una fotografía reciente tipo carnet',
                is_required=True,
                order=1,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='nombres_apellidos',
                label='Nombres y Apellidos',
                field_type='text',
                is_required=True,
                max_length=100,
                order=2,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='documento_identidad',
                label='Documento de Identidad',
                field_type='text',
                is_required=True,
                max_length=20,
                order=3,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='fecha_nacimiento',
                label='Fecha de Nacimiento',
                field_type='date',
                is_required=True,
                order=4,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='edad',
                label='Edad',
                field_type='number',
                is_required=True,
                order=5,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='estado_civil',
                label='Estado Civil',
                field_type='select',
                choices=['Soltero/a', 'Casado/a', 'Divorciado/a', 'Viudo/a', 'Unión Libre'],
                is_required=True,
                order=6,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='direccion_residencia',
                label='Dirección de Residencia',
                field_type='text',
                is_required=True,
                max_length=200,
                order=7,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='telefono',
                label='Teléfono',
                field_type='text',
                is_required=True,
                max_length=15,
                order=8,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='correo_electronico',
                label='Correo Electrónico',
                field_type='email',
                is_required=True,
                order=9,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='ciudad',
                label='Ciudad',
                field_type='text',
                is_required=True,
                max_length=50,
                order=10,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='pais',
                label='País',
                field_type='text',
                is_required=True,
                max_length=50,
                order=11,
                section='Datos Personales'
            )
            
            # Perfil profesional
            FormField.objects.create(
                template=hoja_vida_template,
                name='perfil_profesional',
                label='Perfil Profesional',
                field_type='textarea',
                help_text='Describa brevemente su perfil profesional y objetivos',
                is_required=True,
                order=12,
                section='Perfil Profesional'
            )
            
            # Formación académica (campos JSON para múltiples entradas)
            FormField.objects.create(
                template=hoja_vida_template,
                name='formacion_academica',
                label='Formación Académica',
                field_type='textarea',
                help_text='Nivel | Institución | Título Obtenido | Año de finalización (una por línea)',
                is_required=True,
                order=13,
                section='Formación Académica'
            )
            
            # Experiencia laboral
            FormField.objects.create(
                template=hoja_vida_template,
                name='experiencia_laboral',
                label='Experiencia Laboral',
                field_type='textarea',
                help_text='Empresa | Cargo | Funciones | Fecha inicio | Fecha fin (una por línea)',
                is_required=False,
                order=14,
                section='Experiencia Laboral'
            )
            
            # Referencias personales
            FormField.objects.create(
                template=hoja_vida_template,
                name='referencias_personales',
                label='Referencias Personales',
                field_type='textarea',
                help_text='Nombre | Ocupación | Teléfono | Relación (una por línea)',
                is_required=True,
                order=15,
                section='Referencias'
            )
            
            # Referencias laborales
            FormField.objects.create(
                template=hoja_vida_template,
                name='referencias_laborales',
                label='Referencias Laborales',
                field_type='textarea',
                help_text='Nombre | Empresa | Cargo | Teléfono (una por línea)',
                is_required=False,
                order=16,
                section='Referencias'
            )
            
            # Información adicional
            FormField.objects.create(
                template=hoja_vida_template,
                name='disponibilidad_horarios',
                label='¿Tiene disponibilidad para laborar en horarios rotativos?',
                field_type='radio',
                choices=['Sí', 'No'],
                is_required=True,
                order=17,
                section='Información Adicional'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='vehiculo_propio',
                label='¿Tiene vehículo propio?',
                field_type='radio',
                choices=['Sí', 'No'],
                is_required=True,
                order=18,
                section='Información Adicional'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='aspiracion_salarial',
                label='Aspiración Salarial',
                field_type='text',
                is_required=False,
                order=19,
                section='Información Adicional'
            )
            
            FormField.objects.create(
                template=hoja_vida_template,
                name='fecha_disponibilidad',
                label='Fecha de Disponibilidad',
                field_type='date',
                is_required=True,
                order=20,
                section='Información Adicional'
            )
        
        # ============================================================================
        # 2. REPORTE DE NOVEDADES (OPA-EUEC-11)
        # ============================================================================
        
        novedades_template, created = FormTemplate.objects.get_or_create(
            code='OPA-EUEC-11',
            defaults={
                'title': 'Formulario Reporte de Novedades',
                'description': 'Formulario para reportar novedades, incidentes y situaciones durante el servicio de seguridad.',
                'category': security_category,
                'version': '1.0',
                'is_active': True,
                'requires_approval': True,
                'allow_draft': True,
                'required_permission': 'all',
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write('✅ Plantilla Reporte de Novedades creada')
            
            FormField.objects.create(
                template=novedades_template,
                name='proyecto',
                label='Proyecto',
                field_type='text',
                is_required=True,
                max_length=100,
                order=1,
                section='Información General'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='fecha',
                label='Fecha',
                field_type='date',
                is_required=True,
                order=2,
                section='Información General'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='agente_reporta',
                label='Agente que Reporta',
                field_type='text',
                is_required=True,
                max_length=100,
                order=3,
                section='Información General'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='supervisor_turno',
                label='Supervisor de Turno',
                field_type='text',
                is_required=True,
                max_length=100,
                order=4,
                section='Información General'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='titulo_novedad',
                label='Título de la Novedad',
                field_type='text',
                is_required=True,
                max_length=200,
                order=5,
                section='Detalle del Reporte'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='antecedentes',
                label='Antecedentes',
                field_type='textarea',
                help_text='Describa los antecedentes relevantes',
                is_required=True,
                order=6,
                section='Detalle del Reporte'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='desarrollo',
                label='Desarrollo',
                field_type='textarea',
                help_text='Describa el desarrollo de los eventos',
                is_required=True,
                order=7,
                section='Detalle del Reporte'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='conclusion',
                label='Conclusión',
                field_type='textarea',
                help_text='Conclusiones y recomendaciones',
                is_required=True,
                order=8,
                section='Detalle del Reporte'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='anexos',
                label='Anexos',
                field_type='file',
                help_text='Adjunte documentos, fotos o evidencias',
                is_required=False,
                order=9,
                section='Anexos'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='nombre_reporta',
                label='Nombre de quien Reporta',
                field_type='text',
                is_required=True,
                max_length=100,
                order=10,
                section='Firma y Validación'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='firma_reporta',
                label='Firma de quien Reporta',
                field_type='signature',
                is_required=True,
                order=11,
                section='Firma y Validación'
            )
            
            FormField.objects.create(
                template=novedades_template,
                name='cedula_identidad',
                label='Cédula de Identidad',
                field_type='text',
                is_required=True,
                max_length=20,
                order=12,
                section='Firma y Validación'
            )
        
        # ============================================================================
        # 3. SOLICITUD DE EMPLEO (OP-EUEC-02)
        # ============================================================================
        
        solicitud_template, created = FormTemplate.objects.get_or_create(
            code='OP-EUEC-02',
            defaults={
                'title': 'Formulario de Solicitud de Empleo',
                'description': 'Formulario oficial para solicitar empleo en Euro Security.',
                'category': rrhh_category,
                'version': '1.0',
                'is_active': True,
                'requires_approval': True,
                'allow_draft': True,
                'required_permission': 'hr',
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write('✅ Plantilla Solicitud de Empleo creada')
            
            # Datos personales
            FormField.objects.create(
                template=solicitud_template,
                name='nombre_completo',
                label='Nombre completo',
                field_type='text',
                is_required=True,
                max_length=100,
                order=1,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='fecha_nacimiento',
                label='Fecha de nacimiento',
                field_type='date',
                is_required=True,
                order=2,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='edad',
                label='Edad',
                field_type='number',
                is_required=True,
                order=3,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='estado_civil',
                label='Estado civil',
                field_type='select',
                choices=['Soltero/a', 'Casado/a', 'Divorciado/a', 'Viudo/a', 'Unión Libre'],
                is_required=True,
                order=4,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='direccion',
                label='Dirección',
                field_type='text',
                is_required=True,
                max_length=200,
                order=5,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='telefono',
                label='Teléfono',
                field_type='text',
                is_required=True,
                max_length=15,
                order=6,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='correo_electronico',
                label='Correo electrónico',
                field_type='email',
                is_required=True,
                order=7,
                section='Datos Personales'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='cedula_identidad',
                label='Cédula de identidad',
                field_type='text',
                is_required=True,
                max_length=20,
                order=8,
                section='Datos Personales'
            )
            
            # Puesto solicitado
            FormField.objects.create(
                template=solicitud_template,
                name='puesto_aplica',
                label='Puesto al que aplica',
                field_type='text',
                is_required=True,
                max_length=100,
                order=9,
                section='Puesto Solicitado'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='area_departamento',
                label='Área / Departamento',
                field_type='text',
                is_required=True,
                max_length=100,
                order=10,
                section='Puesto Solicitado'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='sueldo_deseado',
                label='Sueldo deseado',
                field_type='text',
                is_required=False,
                max_length=50,
                order=11,
                section='Puesto Solicitado'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='fecha_puede_empezar',
                label='Fecha en que puede empezar',
                field_type='date',
                is_required=True,
                order=12,
                section='Puesto Solicitado'
            )
            
            # Formación académica
            FormField.objects.create(
                template=solicitud_template,
                name='nivel_estudios',
                label='Nivel de estudios',
                field_type='select',
                choices=['Primaria', 'Secundaria', 'Técnico', 'Tecnológico', 'Universitario', 'Postgrado'],
                is_required=True,
                order=13,
                section='Formación Académica'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='institucion',
                label='Institución',
                field_type='text',
                is_required=True,
                max_length=100,
                order=14,
                section='Formación Académica'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='titulo_certificado',
                label='Título / Certificado',
                field_type='text',
                is_required=True,
                max_length=100,
                order=15,
                section='Formación Académica'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='anos_cursados',
                label='Años cursados',
                field_type='text',
                is_required=True,
                max_length=20,
                order=16,
                section='Formación Académica'
            )
            
            # Experiencia laboral
            FormField.objects.create(
                template=solicitud_template,
                name='experiencia_laboral',
                label='Experiencia Laboral',
                field_type='textarea',
                help_text='Empresa | Puesto | Período | Motivo de salida (una por línea)',
                is_required=False,
                order=17,
                section='Experiencia Laboral'
            )
            
            # Referencias
            FormField.objects.create(
                template=solicitud_template,
                name='referencias',
                label='Referencias Personales/Laborales',
                field_type='textarea',
                help_text='Nombre | Teléfono | Relación (una por línea)',
                is_required=True,
                order=18,
                section='Referencias'
            )
            
            # Información adicional
            FormField.objects.create(
                template=solicitud_template,
                name='experiencia_seguridad',
                label='¿Ha trabajado antes en empresas de seguridad?',
                field_type='radio',
                choices=['Sí', 'No'],
                is_required=True,
                order=19,
                section='Información Adicional'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='disponibilidad_horarios',
                label='¿Tiene disponibilidad para trabajar en horarios rotativos?',
                field_type='radio',
                choices=['Sí', 'No'],
                is_required=True,
                order=20,
                section='Información Adicional'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='disponibilidad_tiempo',
                label='¿Tiene disponibilidad de tiempo?',
                field_type='radio',
                choices=['Sí', 'No'],
                is_required=True,
                order=21,
                section='Información Adicional'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='firma_solicitante',
                label='Firma del solicitante',
                field_type='signature',
                is_required=True,
                order=22,
                section='Firma y Validación'
            )
            
            FormField.objects.create(
                template=solicitud_template,
                name='fecha_solicitud',
                label='Fecha',
                field_type='date',
                is_required=True,
                order=23,
                section='Firma y Validación'
            )
        
        # ============================================================================
        # 4. REGISTRO DE ASISTENCIA A CAPACITACIÓN (OP-EUEC-10)
        # ============================================================================
        
        capacitacion_template, created = FormTemplate.objects.get_or_create(
            code='OP-EUEC-10',
            defaults={
                'title': 'Registro de Asistencia a Capacitación',
                'description': 'Formulario para registrar la asistencia de empleados a capacitaciones y entrenamientos.',
                'category': rrhh_category,
                'version': '1.0',
                'is_active': True,
                'requires_approval': False,
                'allow_draft': True,
                'required_permission': 'hr',
                'created_by': admin_user
            }
        )
        
        if created:
            self.stdout.write('✅ Plantilla Registro de Capacitación creada')
            
            FormField.objects.create(
                template=capacitacion_template,
                name='nombre_instructor',
                label='Nombre del Instructor',
                field_type='text',
                is_required=True,
                max_length=100,
                order=1,
                section='Información de la Capacitación'
            )
            
            FormField.objects.create(
                template=capacitacion_template,
                name='tema_capacitacion',
                label='Tema de la Capacitación',
                field_type='text',
                is_required=True,
                max_length=200,
                order=2,
                section='Información de la Capacitación'
            )
            
            FormField.objects.create(
                template=capacitacion_template,
                name='fecha_capacitacion',
                label='Fecha de la Capacitación',
                field_type='date',
                is_required=True,
                order=3,
                section='Información de la Capacitación'
            )
            
            FormField.objects.create(
                template=capacitacion_template,
                name='duracion',
                label='Duración (horas)',
                field_type='number',
                is_required=True,
                order=4,
                section='Información de la Capacitación'
            )
            
            FormField.objects.create(
                template=capacitacion_template,
                name='asistentes',
                label='Lista de Asistentes',
                field_type='textarea',
                help_text='Nombres | Apellidos | Cédula | Proyecto (uno por línea)',
                is_required=True,
                order=5,
                section='Registro de Asistencia'
            )
            
            FormField.objects.create(
                template=capacitacion_template,
                name='observaciones',
                label='Observaciones',
                field_type='textarea',
                help_text='Observaciones adicionales sobre la capacitación',
                is_required=False,
                order=6,
                section='Observaciones'
            )
        
        # Estadísticas finales
        total_templates = FormTemplate.objects.count()
        total_fields = FormField.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 ¡Formularios dinámicos creados exitosamente!'))
        self.stdout.write(f'📋 Total plantillas: {total_templates}')
        self.stdout.write(f'🔧 Total campos: {total_fields}')
        self.stdout.write(f'\n🔗 Accede al admin: /admin/forms/formtemplate/')
        self.stdout.write(f'🌐 Dashboard: /formularios/dinamicos/')
        
        self.stdout.write(self.style.WARNING('\n📝 NOTA: Recuerda que estos formularios incluirán el letterhead.jpg'))
        self.stdout.write('   cuando se exporten a PDF desde el sistema.')
