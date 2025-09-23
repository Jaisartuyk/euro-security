#!/usr/bin/env python
"""
Script para configurar variables de entorno en Railway
"""
import subprocess
import sys

def set_railway_variables():
    variables = {
        'SECRET_KEY': '^@o*8&1_ou%em9$_#(8e37in^h=n05ki75kl_dgjozut^lr2do',
        'DEBUG': 'True',
        'ALLOWED_HOSTS': 'euro-security-production.up.railway.app,high-pitched-fuel-production.up.railway.app',
        'GOOGLE_MAPS_API_KEY': 'AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ',
        'LANGUAGE_CODE': 'es-ec'
    }
    
    print("🚂 Configurando variables de entorno en Railway...")
    
    for key, value in variables.items():
        try:
            cmd = f'railway variables set {key}="{value}"'
            print(f"⚙️ Configurando {key}...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {key} configurado exitosamente")
            else:
                print(f"❌ Error configurando {key}: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error con {key}: {e}")
    
    print("\n🎯 Variables configuradas. Railway hará redeploy automáticamente.")
    print("⏰ Espera 2-3 minutos y prueba: https://euro-security-production.up.railway.app")

if __name__ == '__main__':
    set_railway_variables()
