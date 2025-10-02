from django.core.management.base import BaseCommand
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os


class Command(BaseCommand):
    help = 'Generar PDF del Formulario de Entrevista Laboral'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📄 Generando PDF del Formulario de Entrevista Laboral...'))
        
        # Crear directorio si no existe
        forms_dir = os.path.join(settings.MEDIA_ROOT, 'forms', 'documents')
        os.makedirs(forms_dir, exist_ok=True)
        
        # Ruta del archivo PDF
        pdf_path = os.path.join(forms_dir, 'formulario_entrevista_laboral_OP-EUEC-01.pdf')
        
        # Crear el documento PDF
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo personalizado para el título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # Estilo para subtítulos
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.darkblue,
            backColor=colors.lightgrey,
            borderPadding=5
        )
        
        # Estilo para texto normal
        normal_style = styles['Normal']
        normal_style.fontSize = 10
        normal_style.spaceAfter = 6
        
        # Contenido del PDF
        story = []
        
        # Encabezado con información del formulario
        header_data = [
            ['FORMULARIO DE ENTREVISTA LABORAL', '', '', ''],
            ['Codificación', 'Versión', 'Emisión', 'Revisión'],
            ['OP-EUEC-01', '1', '09-09-2025', 'XXXXXX']
        ]
        
        header_table = Table(header_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        header_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (3, 0)),
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (3, 0), 14),
            ('TEXTCOLOR', (0, 0), (3, 0), colors.darkblue),
            ('BACKGROUND', (0, 1), (3, 1), colors.lightgrey),
            ('FONTNAME', (0, 1), (3, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (3, 2), 10),
            ('ALIGN', (0, 1), (3, 2), 'CENTER'),
            ('GRID', (0, 0), (3, 2), 1, colors.black),
            ('VALIGN', (0, 0), (3, 2), 'MIDDLE'),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
        
        # Datos del Candidato
        story.append(Paragraph("Datos del Candidato", subtitle_style))
        
        candidate_data = [
            ['Nombre:', '_' * 60],
            ['Puesto al que aplica:', '_' * 40],
            ['Fecha:', '___/___/______', 'Entrevistador:', '_' * 30]
        ]
        
        candidate_table = Table(candidate_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
        candidate_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(candidate_table)
        story.append(Spacer(1, 15))
        
        # Secciones del formulario
        sections = [
            {
                'title': '1. Presentación General',
                'items': [
                    'Puntualidad: ☐ Sí ☐ No',
                    'Apariencia profesional: ☐ Excelente ☐ Buena ☐ Regular ☐ Deficiente',
                    'Actitud inicial: ☐ Positiva ☐ Neutral ☐ Negativa',
                    'Observaciones: ' + '_' * 50
                ]
            },
            {
                'title': '2. Formación Académica',
                'items': [
                    'Nivel de estudios alcanzado: ' + '_' * 30,
                    'Relevancia para el puesto: ☐ Alta ☐ Media ☐ Baja',
                    'Comentarios: ' + '_' * 50
                ]
            },
            {
                'title': '3. Experiencia Laboral',
                'items': [
                    'Experiencia previa en puestos similares: ☐ Sí ☐ No',
                    'Tiempo de experiencia: ' + '_' * 30,
                    'Logros relevantes: ' + '_' * 35,
                    'Comentarios: ' + '_' * 50
                ]
            },
            {
                'title': '4. Habilidades y Competencias',
                'items': [
                    'Comunicación: ☐ Excelente ☐ Buena ☐ Regular ☐ Deficiente',
                    'Trabajo en equipo: ☐ Excelente ☐ Buena ☐ Regular ☐ Deficiente',
                    'Resolución de problemas: ☐ Excelente ☐ Buena ☐ Regular ☐ Deficiente',
                    'Liderazgo (si aplica): ☐ Excelente ☐ Buena ☐ Regular ☐ Deficiente',
                    'Comentarios: ' + '_' * 50
                ]
            },
            {
                'title': '5. Motivación y Expectativas',
                'items': [
                    'Razón principal para postularse: ' + '_' * 25,
                    'Expectativa salarial: ' + '_' * 35,
                    'Disponibilidad de horario: ☐ Sí ☐ No',
                    'Interés en crecer dentro de la empresa: ☐ Sí ☐ No',
                    'Comentarios: ' + '_' * 50
                ]
            },
            {
                'title': '6. Evaluación Final del Entrevistador',
                'items': [
                    'Nivel de adecuación al puesto:',
                    '☐ Muy adecuado',
                    '☐ Adecuado',
                    '☐ Poco adecuado',
                    '☐ No adecuado',
                    '',
                    'Recomendación:',
                    '☐ Continuar en proceso',
                    '☐ Rechazar candidato',
                    '☐ Mantener en base de datos',
                    '',
                    'Firma del entrevistador: ' + '_' * 35
                ]
            }
        ]
        
        # Agregar cada sección
        for section in sections:
            story.append(Paragraph(section['title'], subtitle_style))
            
            for item in section['items']:
                if item.strip():  # Solo agregar si no está vacío
                    story.append(Paragraph(item, normal_style))
                else:
                    story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 10))
        
        # Generar el PDF
        doc.build(story)
        
        self.stdout.write(self.style.SUCCESS(f'✅ PDF generado exitosamente: {pdf_path}'))
        self.stdout.write(f'📁 Ubicación: {pdf_path}')
        self.stdout.write(f'📄 Tamaño: {os.path.getsize(pdf_path)} bytes')
        
        return pdf_path
