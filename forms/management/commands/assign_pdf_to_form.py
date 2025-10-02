from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from forms.models import FormDocument
import os


class Command(BaseCommand):
    help = 'Asignar PDF generado al formulario de entrevista en la base de datos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📎 Asignando PDF al formulario de entrevista...'))
        
        # Buscar el formulario de entrevista
        try:
            form = FormDocument.objects.get(title='Formulario de Entrevista Laboral')
        except FormDocument.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Formulario de entrevista no encontrado'))
            return
        
        # Ruta del PDF generado
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'forms', 'documents', 'formulario_entrevista_laboral_OP-EUEC-01.pdf')
        
        if not os.path.exists(pdf_path):
            self.stdout.write(self.style.ERROR(f'❌ PDF no encontrado: {pdf_path}'))
            return
        
        # Asignar el archivo al formulario
        try:
            with open(pdf_path, 'rb') as pdf_file:
                django_file = File(pdf_file)
                form.file.save(
                    'formulario_entrevista_laboral_OP-EUEC-01.pdf',
                    django_file,
                    save=True
                )
            
            # Actualizar metadatos del archivo
            form.file_size = os.path.getsize(pdf_path)
            form.file_type = 'PDF'
            form.save()
            
            self.stdout.write(self.style.SUCCESS('✅ PDF asignado exitosamente al formulario'))
            self.stdout.write(f'📄 Archivo: {form.file.name}')
            self.stdout.write(f'📊 Tamaño: {form.get_file_size_display()}')
            self.stdout.write(f'🔗 URL de descarga: /formularios/descargar/{form.id}/')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error al asignar PDF: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS('\n🎉 ¡Formulario listo para descargar!'))
        self.stdout.write('🌐 Accede a /formularios/ para probarlo')
