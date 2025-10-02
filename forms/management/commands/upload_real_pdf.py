from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from forms.models import FormDocument
import os


class Command(BaseCommand):
    help = 'Subir PDF real del formulario de entrevista desde archivo local'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📄 Subiendo PDF real del formulario...'))
        
        # Buscar el PDF local generado
        local_pdf_path = os.path.join(settings.MEDIA_ROOT, 'forms', 'documents', 'formulario_entrevista_laboral_OP-EUEC-01.pdf')
        
        if not os.path.exists(local_pdf_path):
            self.stdout.write(self.style.ERROR(f'❌ PDF local no encontrado: {local_pdf_path}'))
            self.stdout.write('🔧 Ejecuta primero: python manage.py generate_interview_form_pdf')
            return
        
        try:
            # Buscar el formulario
            form = FormDocument.objects.get(title='Formulario de Entrevista Laboral')
            
            # Leer el PDF local
            with open(local_pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            # Crear ContentFile
            django_file = ContentFile(pdf_content, name='formulario_entrevista_laboral_OP-EUEC-01.pdf')
            
            # Limpiar archivo anterior si existe
            if form.file:
                form.file.delete(save=False)
            
            # Asignar nuevo archivo
            form.file.save('formulario_entrevista_laboral_OP-EUEC-01.pdf', django_file, save=False)
            form.file_size = len(pdf_content)
            form.file_type = 'PDF'
            form.save()
            
            self.stdout.write(self.style.SUCCESS('✅ PDF real subido exitosamente'))
            self.stdout.write(f'📄 Archivo: {form.file.name}')
            self.stdout.write(f'📊 Tamaño: {form.get_file_size_display()}')
            self.stdout.write(f'🔗 ID: {form.id}')
            
            # Verificar
            if form.file and os.path.exists(form.file.path):
                self.stdout.write(self.style.SUCCESS('✅ Archivo verificado'))
            else:
                self.stdout.write(self.style.ERROR('❌ Error en verificación'))
            
        except FormDocument.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Formulario no encontrado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎯 URLs para probar:'))
        self.stdout.write('👁️ Vista previa: https://euro-security-production.up.railway.app/formularios/preview/1/')
        self.stdout.write('📥 Descarga: https://euro-security-production.up.railway.app/formularios/descargar/1/')
        self.stdout.write('📋 Dashboard: https://euro-security-production.up.railway.app/formularios/')
