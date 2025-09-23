ien #!/usr/bin/env python3
"""
Script para crear iconos PWA básicos
EURO SECURITY - Create PWA Icons
"""
import os
from PIL import Image, ImageDraw, ImageFont

def create_pwa_icons():
    """Crear iconos PWA básicos para EURO SECURITY"""
    print("🎨 Creando iconos PWA para EURO SECURITY...")
    
    # Crear directorio de iconos
    icons_dir = "static/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # Tamaños de iconos necesarios
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        # Crear imagen
        img = Image.new('RGB', (size, size), color='#3b82f6')
        draw = ImageDraw.Draw(img)
        
        # Círculo blanco de fondo
        margin = size // 8
        draw.ellipse([margin, margin, size-margin, size-margin], fill='white')
        
        # Texto "ES" (EURO SECURITY)
        try:
            # Intentar usar fuente del sistema
            font_size = size // 4
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Usar fuente por defecto si no encuentra arial
            font = ImageFont.load_default()
        
        # Calcular posición del texto
        text = "ES"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        # Dibujar texto
        draw.text((x, y), text, fill='#3b82f6', font=font)
        
        # Guardar icono
        filename = f"{icons_dir}/icon-{size}x{size}.png"
        img.save(filename)
        print(f"  ✅ Creado: {filename}")
    
    # Crear badge icon (pequeño para notificaciones)
    badge_img = Image.new('RGB', (72, 72), color='#dc3545')
    badge_draw = ImageDraw.Draw(badge_img)
    badge_draw.ellipse([10, 10, 62, 62], fill='white')
    badge_draw.text((25, 25), "!", fill='#dc3545', font=font)
    badge_img.save(f"{icons_dir}/badge-72x72.png")
    print(f"  ✅ Creado: {icons_dir}/badge-72x72.png")
    
    print("🎉 ¡Iconos PWA creados exitosamente!")
    return True

if __name__ == "__main__":
    create_pwa_icons()
