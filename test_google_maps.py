#!/usr/bin/env python3
"""
Script para probar la API Key de Google Maps
EURO SECURITY - Test Google Maps
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'security_hr_system.settings')
sys.path.append('.')
django.setup()

from django.conf import settings
import requests

def test_google_maps_api():
    """Probar la API Key de Google Maps"""
    print("🗺️ EURO SECURITY - Test Google Maps API")
    print("=" * 45)
    
    try:
        # Obtener API Key desde settings
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
        
        print(f"🔑 API Key configurada: {api_key[:20]}...{api_key[-10:] if api_key else 'No encontrada'}")
        
        if not api_key:
            print("❌ No hay API Key configurada en settings.py")
            return
        
        # Probar la API con una geocodificación simple
        print(f"\n🔍 Probando API de Geocodificación...")
        
        geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': 'Bogotá, Colombia',
            'key': api_key
        }
        
        response = requests.get(geocode_url, params=params)
        data = response.json()
        
        print(f"📡 Status Code: {response.status_code}")
        print(f"📊 Response Status: {data.get('status', 'Unknown')}")
        
        if data.get('status') == 'OK':
            print("✅ API Key funciona correctamente")
            results = data.get('results', [])
            if results:
                location = results[0]['geometry']['location']
                print(f"📍 Ubicación de prueba: {location['lat']}, {location['lng']}")
        elif data.get('status') == 'REQUEST_DENIED':
            print("❌ API Key denegada - Verifica permisos")
            print(f"💡 Error: {data.get('error_message', 'Sin mensaje de error')}")
        elif data.get('status') == 'INVALID_REQUEST':
            print("❌ Solicitud inválida")
        else:
            print(f"⚠️ Estado desconocido: {data.get('status')}")
            print(f"💡 Mensaje: {data.get('error_message', 'Sin mensaje')}")
        
        # Verificar servicios necesarios
        print(f"\n🛠️ SERVICIOS NECESARIOS PARA EL MAPA:")
        print(f"   📍 Maps JavaScript API - Para mostrar mapas")
        print(f"   🔍 Geocoding API - Para direcciones")
        print(f"   📊 Places API - Para información de lugares (opcional)")
        
        print(f"\n🔧 SI EL MAPA SE VE AZUL:")
        print(f"   1. Ve a Google Cloud Console")
        print(f"   2. Habilita 'Maps JavaScript API'")
        print(f"   3. Verifica que la API Key tenga permisos")
        print(f"   4. Revisa las restricciones de dominio")
        
        print(f"\n🌐 URLS PARA CONFIGURAR:")
        print(f"   Google Cloud Console: https://console.cloud.google.com/")
        print(f"   APIs & Services: https://console.cloud.google.com/apis/")
        
        # Crear HTML de prueba simple
        html_test = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Google Maps - EURO SECURITY</title>
    <style>
        #map {{ height: 400px; width: 100%; }}
        .info {{ padding: 20px; font-family: Arial; }}
    </style>
</head>
<body>
    <div class="info">
        <h2>🗺️ Test Google Maps API</h2>
        <p><strong>API Key:</strong> {api_key[:20]}...{api_key[-10:]}</p>
        <p><strong>Estado:</strong> <span id="status">Cargando...</span></p>
    </div>
    <div id="map"></div>
    
    <script>
        function initMap() {{
            document.getElementById('status').innerHTML = '✅ API Key funcionando';
            
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 10,
                center: {{lat: 4.7110, lng: -74.0721}} // Bogotá
            }});
            
            var marker = new google.maps.Marker({{
                position: {{lat: 4.7110, lng: -74.0721}},
                map: map,
                title: 'EURO SECURITY - Oficina Principal'
            }});
        }}
        
        window.gm_authFailure = function() {{
            document.getElementById('status').innerHTML = '❌ Error de autenticación';
            document.getElementById('map').innerHTML = '<div style="padding:20px;text-align:center;background:#f8d7da;color:#721c24;border:1px solid #f5c6cb;">Error: Verifica la API Key de Google Maps</div>';
        }};
    </script>
    
    <script async defer 
            src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap">
    </script>
</body>
</html>
        """
        
        # Guardar archivo de prueba
        with open('test_google_maps.html', 'w', encoding='utf-8') as f:
            f.write(html_test)
        
        print(f"\n📄 Archivo de prueba creado: test_google_maps.html")
        print(f"   Abre este archivo en tu navegador para probar el mapa")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_google_maps_api()
