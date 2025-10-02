from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from forms.models import FormDocument
import os


class Command(BaseCommand):
    help = 'Verificar y corregir la subida del PDF al formulario'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando estado del formulario...'))
        
        try:
            form = FormDocument.objects.get(title='Formulario de Entrevista Laboral')
            self.stdout.write(f'✅ Formulario encontrado: {form.title}')
            
            # Verificar estado actual del archivo
            if form.file:
                self.stdout.write(f'📄 Archivo actual: {form.file.name}')
                if os.path.exists(form.file.path):
                    self.stdout.write(f'✅ Archivo existe en: {form.file.path}')
                    self.stdout.write(f'📊 Tamaño: {os.path.getsize(form.file.path)} bytes')
                else:
                    self.stdout.write(f'❌ Archivo no existe en: {form.file.path}')
            else:
                self.stdout.write('❌ No hay archivo asignado')
            
            # Buscar el PDF generado localmente
            local_pdf_path = os.path.join(settings.MEDIA_ROOT, 'forms', 'documents', 'formulario_entrevista_laboral_OP-EUEC-01.pdf')
            
            if os.path.exists(local_pdf_path):
                self.stdout.write(f'✅ PDF local encontrado: {local_pdf_path}')
                self.stdout.write(f'📊 Tamaño local: {os.path.getsize(local_pdf_path)} bytes')
                
                # Leer el archivo y asignarlo al formulario
                with open(local_pdf_path, 'rb') as pdf_file:
                    pdf_content = pdf_file.read()
                    
                # Crear ContentFile y asignarlo
                django_file = ContentFile(pdf_content, name='formulario_entrevista_laboral_OP-EUEC-01.pdf')
                form.file.save('formulario_entrevista_laboral_OP-EUEC-01.pdf', django_file, save=False)
                
                # Actualizar metadatos
                form.file_size = len(pdf_content)
                form.file_type = 'PDF'
                form.save()
                
                self.stdout.write(self.style.SUCCESS('✅ PDF asignado correctamente al formulario'))
                self.stdout.write(f'📄 Nuevo archivo: {form.file.name}')
                self.stdout.write(f'📊 Tamaño: {form.get_file_size_display()}')
                
            else:
                self.stdout.write(f'❌ PDF local no encontrado en: {local_pdf_path}')
                self.stdout.write('🔧 Ejecuta: python manage.py generate_interview_form_pdf')
                return
            
        except FormDocument.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Formulario no encontrado'))
            self.stdout.write('🔧 Ejecuta: railway run python manage.py create_euro_security_forms')
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            return
        
        # Verificar URLs
        self.stdout.write(self.style.SUCCESS('\n🔗 URLs disponibles:'))
        self.stdout.write(f'👁️ Vista previa: /formularios/preview/{form.id}/')
        self.stdout.write(f'📥 Descarga: /formularios/descargar/{form.id}/')
        self.stdout.write(f'📋 Dashboard: /formularios/')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Formulario listo para usar!'))
