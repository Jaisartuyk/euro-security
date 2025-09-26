#!/usr/bin/env python3
"""
Crear iconos faltantes para PWA shortcuts
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(output_path, icon_type, size=96):
    """Crear icono específico para shortcuts"""
    
    # Colores
    bg_color = (30, 58, 138, 255)  # Azul EURO SECURITY
    icon_color = (255, 255, 255, 255)  # Blanco
    
    # Crear imagen
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Configurar según el tipo de icono
    if icon_type == 'clock':
        # Dibujar reloj
        center = size // 2
        radius = size // 3
        
        # Círculo exterior
        draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                    outline=icon_color, width=3)
        
        # Manecillas
        draw.line([center, center, center, center-radius//2], fill=icon_color, width=2)  # Hora
        draw.line([center, center, center+radius//3, center], fill=icon_color, width=2)  # Minuto
        
        # Centro
        draw.ellipse([center-3, center-3, center+3, center+3], fill=icon_color)
        
    elif icon_type == 'history':
        # Dibujar historial (líneas)
        margin = size // 4
        line_height = 4
        spacing = 8
        
        for i in range(5):
            y = margin + i * (line_height + spacing)
            width = size - 2*margin - (i * 10)  # Líneas de diferente longitud
            draw.rectangle([margin, y, margin + width, y + line_height], fill=icon_color)
            
    elif icon_type == 'gps':
        # Dibujar GPS (punto con ondas)
        center = size // 2
        
        # Punto central
        draw.ellipse([center-4, center-4, center+4, center+4], fill=icon_color)
        
        # Ondas concéntricas
        for radius in [12, 20, 28]:
            draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                        outline=icon_color, width=2)
    
    # Guardar
    img.save(output_path, 'PNG', optimize=True)
    print(f"✅ Creado: {output_path}")

def main():
    print("🎨 Creando iconos faltantes para PWA")
    
    icons_dir = "static/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Crear iconos faltantes
    icons_to_create = [
        ('clock-icon.png', 'clock'),
        ('history-icon.png', 'history'),
        ('gps-icon.png', 'gps')
    ]
    
    for filename, icon_type in icons_to_create:
        output_path = os.path.join(icons_dir, filename)
        create_icon(output_path, icon_type)
    
    print("🎊 ¡Iconos creados exitosamente!")

if __name__ == "__main__":
    main()
