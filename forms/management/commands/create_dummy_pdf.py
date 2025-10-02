from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from forms.models import FormDocument
import os


class Command(BaseCommand):
    help = 'Crear un PDF dummy para el formulario de entrevista'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📄 Creando PDF dummy para formulario...'))
        
        # Contenido PDF básico (header PDF válido)
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
50 750 Td
(FORMULARIO DE ENTREVISTA LABORAL) Tj
0 -20 Td
(Euro Security - Codigo: OP-EUEC-01) Tj
0 -40 Td
(Este es un PDF de prueba.) Tj
0 -20 Td
(Descarga el formulario completo desde el admin.) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000526 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
623
%%EOF"""
        
        try:
            # Buscar el formulario
            form = FormDocument.objects.get(title='Formulario de Entrevista Laboral')
            
            # Crear ContentFile con el PDF
            pdf_file = ContentFile(pdf_content, name='formulario_entrevista_laboral_OP-EUEC-01.pdf')
            
            # Asignar al formulario
            form.file.save('formulario_entrevista_laboral_OP-EUEC-01.pdf', pdf_file, save=False)
            form.file_size = len(pdf_content)
            form.file_type = 'PDF'
            form.save()
            
            self.stdout.write(self.style.SUCCESS('✅ PDF dummy creado y asignado'))
            self.stdout.write(f'📄 Archivo: {form.file.name}')
            self.stdout.write(f'📊 Tamaño: {form.get_file_size_display()}')
            self.stdout.write(f'🔗 ID del formulario: {form.id}')
            
            # Verificar que existe
            if os.path.exists(form.file.path):
                self.stdout.write(self.style.SUCCESS('✅ Archivo verificado - existe físicamente'))
            else:
                self.stdout.write(self.style.ERROR('❌ Archivo no existe físicamente'))
            
        except FormDocument.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Formulario no encontrado'))
            self.stdout.write('🔧 Ejecuta primero: railway run python manage.py create_euro_security_forms')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n🎯 Prueba ahora:'))
        self.stdout.write('👁️ Vista previa: /formularios/preview/1/')
        self.stdout.write('📥 Descarga: /formularios/descargar/1/')
