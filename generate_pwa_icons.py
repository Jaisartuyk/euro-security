#!/usr/bin/env python3
"""
Generador de iconos PWA para EURO SECURITY
Convierte el logo principal en todos los tamaños necesarios para PWA
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import json

# Configuración
LOGO_PATH = "static/images/logos/euro-security-icon.jpg"  # Tu logo cuadrado
ICONS_DIR = "static/icons/"
COMPANY_NAME = "EURO SECURITY"

# Tamaños requeridos para PWA
ICON_SIZES = [
    72, 96, 128, 144, 152, 192, 384, 512
]

def create_pwa_icon(logo_path, output_path, size, add_background=True):
    """Crea un icono PWA desde el logo"""
    try:
        # Abrir el logo original
        with Image.open(logo_path) as logo:
            # Convertir a RGBA si no lo está
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Crear imagen cuadrada con fondo
            icon = Image.new('RGBA', (size, size), (30, 58, 138, 255))  # Azul EURO SECURITY
            
            # Calcular tamaño del logo (80% del icono)
            logo_size = int(size * 0.8)
            logo_resized = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Centrar el logo
            x = (size - logo_size) // 2
            y = (size - logo_size) // 2
            
            # Pegar el logo
            icon.paste(logo_resized, (x, y), logo_resized)
            
            # Guardar
            icon.save(output_path, 'PNG', optimize=True)
            print(f"✅ Creado: {output_path} ({size}x{size})")
            
    except Exception as e:
        print(f"❌ Error creando {output_path}: {e}")

def generate_all_icons():
    """Genera todos los iconos PWA"""
    print(f"🎨 Generando iconos PWA para {COMPANY_NAME}")
    print(f"📁 Logo fuente: {LOGO_PATH}")
    print(f"📁 Directorio destino: {ICONS_DIR}")
    
    # Verificar que existe el logo
    if not os.path.exists(LOGO_PATH):
        print(f"❌ Error: No se encuentra el logo en {LOGO_PATH}")
        print("💡 Asegúrate de que el archivo euro-security-icon.jpg existe")
        return False
    
    # Crear directorio de iconos si no existe
    os.makedirs(ICONS_DIR, exist_ok=True)
    
    # Generar cada tamaño
    success_count = 0
    for size in ICON_SIZES:
        output_path = os.path.join(ICONS_DIR, f"icon-{size}x{size}.png")
        create_pwa_icon(LOGO_PATH, output_path, size)
        success_count += 1
    
    # Crear badge especial
    badge_path = os.path.join(ICONS_DIR, "badge-72x72.png")
    create_pwa_icon(LOGO_PATH, badge_path, 72)
    
    print(f"\n🎊 ¡Completado! {success_count} iconos generados exitosamente")
    print(f"📱 Los iconos PWA están listos en: {ICONS_DIR}")
    
    return True

def update_manifest():
    """Actualiza el manifest.json con información de branding"""
    manifest_path = "static/manifest.json"
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Actualizar información
        manifest.update({
            "name": f"{COMPANY_NAME} - Control de Asistencias",
            "short_name": COMPANY_NAME,
            "description": "Sistema de control de asistencias con reconocimiento facial y rastreo GPS en tiempo real",
        })
        
        # Guardar
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Manifest.json actualizado")
        
    except Exception as e:
        print(f"❌ Error actualizando manifest: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🏢 GENERADOR DE ICONOS PWA - EURO SECURITY")
    print("=" * 50)
    
    try:
        # Verificar PIL
        from PIL import Image
        print("✅ PIL/Pillow disponible")
        
        # Generar iconos
        if generate_all_icons():
            update_manifest()
            print("\n🚀 ¡PWA actualizada con branding de EURO SECURITY!")
            print("💡 Ahora puedes instalar la app con tus logos personalizados")
        
    except ImportError:
        print("❌ Error: PIL/Pillow no está instalado")
        print("💡 Instala con: pip install Pillow")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
