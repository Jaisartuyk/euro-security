"""
Utilidades para exportar formularios completados a PDF con letterhead
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
import os
from django.conf import settings


def generate_submission_pdf(submission):
    """
    Genera un PDF con los datos del formulario completado
    
    Args:
        submission: Instancia de FormSubmission
        
    Returns:
        BytesIO: Buffer con el contenido del PDF
    """
    # Crear buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Contenedor para los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    normal_style = styles['Normal']
    
    # Agregar letterhead si existe
    letterhead_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'branding', 'letterhead.jpg')
    if os.path.exists(letterhead_path):
        try:
            img = Image(letterhead_path, width=6*inch, height=1*inch)
            elements.append(img)
            elements.append(Spacer(1, 0.3*inch))
        except Exception as e:
            print(f"Error loading letterhead: {e}")
    
    # Título del formulario
    elements.append(Paragraph(submission.template.title, title_style))
    elements.append(Paragraph(f"Código: {submission.template.code}", normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Información del envío
    info_data = [
        ['Enviado por:', submission.submitted_by.get_full_name()],
        ['Fecha de envío:', submission.submitted_at.strftime('%d/%m/%Y %H:%M') if submission.submitted_at else 'N/A'],
        ['Estado:', submission.get_status_display()],
    ]
    
    if submission.reviewed_by:
        info_data.append(['Revisado por:', submission.reviewed_by.get_full_name()])
        info_data.append(['Fecha de revisión:', submission.reviewed_at.strftime('%d/%m/%Y %H:%M')])
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Datos del formulario por sección
    fields_by_section = {}
    for field in submission.template.fields.all().order_by('section', 'order'):
        section = field.section or 'Información General'
        if section not in fields_by_section:
            fields_by_section[section] = []
        fields_by_section[section].append(field)
    
    for section_name, fields in fields_by_section.items():
        # Título de sección
        elements.append(Paragraph(section_name, heading_style))
        
        # Datos de la sección
        section_data = []
        for field in fields:
            value = submission.form_data.get(field.name, 'Sin respuesta')
            
            # Formatear valor según tipo de campo
            if field.field_type == 'checkbox':
                value = 'Sí' if value else 'No'
            elif field.field_type == 'signature':
                value = '[Firma digital]' if value else 'Sin firma'
            elif field.field_type == 'file':
                value = f'[Archivo: {value}]' if value else 'Sin archivo'
            
            section_data.append([
                Paragraph(f"<b>{field.label}:</b>", normal_style),
                Paragraph(str(value), normal_style)
            ])
        
        section_table = Table(section_data, colWidths=[2.5*inch, 3.5*inch])
        section_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        
        elements.append(section_table)
        elements.append(Spacer(1, 0.2*inch))
    
    # Comentarios de revisión si existen
    if submission.review_comments:
        elements.append(Paragraph("Comentarios de Revisión", heading_style))
        elements.append(Paragraph(submission.review_comments, normal_style))
    
    # Construir PDF
    doc.build(elements)
    
    # Retornar buffer
    buffer.seek(0)
    return buffer
