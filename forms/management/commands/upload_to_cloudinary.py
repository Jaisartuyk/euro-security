from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from forms.models import FormDocument
import cloudinary.uploader
import os


class Command(BaseCommand):
    help = 'Subir PDF a Cloudinary y asignar al formulario'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('☁️ Subiendo PDF a Cloudinary...'))
        
        # Buscar el PDF local
        local_pdf_path = os.path.join(settings.MEDIA_ROOT, 'forms', 'documents', 'formulario_entrevista_laboral_OP-EUEC-01.pdf')
        
        if not os.path.exists(local_pdf_path):
            self.stdout.write(self.style.ERROR(f'❌ PDF local no encontrado: {local_pdf_path}'))
            return
        
        try:
            # Subir a Cloudinary
            self.stdout.write('📤 Subiendo archivo a Cloudinary...')
            result = cloudinary.uploader.upload(
                local_pdf_path,
                resource_type="raw",  # Para archivos no-imagen
                public_id="forms/formulario_entrevista_laboral_OP-EUEC-01",
                folder="euro_security/forms"
            )
            
            self.stdout.write(f'✅ Archivo subido a Cloudinary: {result["secure_url"]}')
            
            # Buscar el formulario
            form = FormDocument.objects.get(title='Formulario de Entrevista Laboral')
            
            # Leer el PDF local para obtener el contenido
            with open(local_pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            # Crear ContentFile con la URL de Cloudinary
            django_file = ContentFile(pdf_content, name='formulario_entrevista_laboral_OP-EUEC-01.pdf')
            
            # Limpiar archivo anterior
            if form.file:
                form.file.delete(save=False)
            
            # Asignar nuevo archivo
            form.file.save('formulario_entrevista_laboral_OP-EUEC-01.pdf', django_file, save=False)
            form.file_size = len(pdf_content)
            form.file_type = 'PDF'
            form.save()
            
            self.stdout.write(self.style.SUCCESS('✅ PDF asignado al formulario'))
            self.stdout.write(f'📄 Archivo: {form.file.name}')
            self.stdout.write(f'📊 Tamaño: {form.get_file_size_display()}')
            self.stdout.write(f'☁️ URL Cloudinary: {result["secure_url"]}')
            
        except FormDocument.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Formulario no encontrado'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎯 URLs para probar:'))
        self.stdout.write('👁️ Vista previa: https://euro-security-production.up.railway.app/formularios/preview/1/')
        self.stdout.write('📥 Descarga: https://euro-security-production.up.railway.app/formularios/descargar/1/')
