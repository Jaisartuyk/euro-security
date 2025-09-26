#!/usr/bin/env python3
"""
Crear favicon.ico desde el logo de EURO SECURITY
"""

import os
from PIL import Image

def create_favicon():
    """Crear favicon.ico desde el logo"""
    
    logo_path = "static/images/logos/euro-security-icon.jpg"
    favicon_path = "static/images/logos/favicon.ico"
    
    if not os.path.exists(logo_path):
        print(f"❌ Logo no encontrado: {logo_path}")
        return False
    
    try:
        # Abrir logo
        with Image.open(logo_path) as logo:
            # Convertir a RGBA si no lo está
            if logo.mode != 'RGBA':
                logo = logo.convert('RGBA')
            
            # Redimensionar a 32x32 (tamaño estándar de favicon)
            favicon = logo.resize((32, 32), Image.Resampling.LANCZOS)
            
            # Guardar como ICO
            favicon.save(favicon_path, format='ICO', sizes=[(32, 32)])
            
            print(f"✅ Favicon creado: {favicon_path}")
            return True
            
    except Exception as e:
        print(f"❌ Error creando favicon: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Creando favicon desde logo EURO SECURITY")
    create_favicon()
