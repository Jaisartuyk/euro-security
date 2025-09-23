#!/usr/bin/env python3
"""
Script para probar las APIs del mapa
"""
import requests
import json

def test_apis():
    """Probar las APIs necesarias para el mapa"""
    print("🔍 PROBANDO APIs DEL MAPA...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Crear sesión para mantener cookies
    session = requests.Session()
    
    # 1. Hacer login primero
    print("\n1. 🔐 Haciendo login...")
    login_url = f"{base_url}/login/"
    
    # Obtener CSRF token
    response = session.get(login_url)
    if response.status_code != 200:
        print(f"❌ Error obteniendo página de login: {response.status_code}")
        return False
    
    # Extraer CSRF token (método simple)
    csrf_token = None
    for line in response.text.split('\n'):
        if 'csrfmiddlewaretoken' in line and 'value=' in line:
            start = line.find('value="') + 7
            end = line.find('"', start)
            csrf_token = line[start:end]
            break
    
    if not csrf_token:
        print("❌ No se pudo obtener CSRF token")
        return False
    
    # Hacer login
    login_data = {
        'username': 'jairo',  # Tu superusuario
        'password': input("Ingresa la contraseña del superusuario 'jairo': "),
        'csrfmiddlewaretoken': csrf_token
    }
    
    response = session.post(login_url, data=login_data)
    if response.status_code != 302 and 'dashboard' not in response.url:
        print(f"❌ Error en login: {response.status_code}")
        return False
    
    print("✅ Login exitoso")
    
    # 2. Probar API de áreas de trabajo
    print("\n2. 🏢 Probando API de áreas de trabajo...")
    areas_url = f"{base_url}/asistencia/api/areas-trabajo/"
    
    response = session.get(areas_url)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ Áreas encontradas: {data.get('total', 0)}")
            if data.get('areas'):
                for area in data['areas'][:2]:  # Mostrar primeras 2
                    print(f"      - {area['name']}: {area['latitude']}, {area['longitude']}")
        except json.JSONDecodeError:
            print(f"   ❌ Respuesta no es JSON válido")
            print(f"   Respuesta: {response.text[:200]}...")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}...")
    
    # 3. Probar API de rastreo GPS
    print("\n3. 🛰️ Probando API de rastreo GPS...")
    gps_url = f"{base_url}/asistencia/api/rastreo-gps/"
    
    response = session.get(gps_url)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ Ubicaciones activas: {data.get('total_active', 0)}")
            if data.get('locations'):
                for loc in data['locations'][:2]:  # Mostrar primeras 2
                    print(f"      - {loc['employee_name']}: {loc['latitude']}, {loc['longitude']}")
        except json.JSONDecodeError:
            print(f"   ❌ Respuesta no es JSON válido")
            print(f"   Respuesta: {response.text[:200]}...")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Respuesta: {response.text[:200]}...")
    
    print(f"\n🎯 RESUMEN:")
    print(f"   🔐 Login: ✅")
    print(f"   🏢 API Áreas: {'✅' if session.get(areas_url).status_code == 200 else '❌'}")
    print(f"   🛰️ API GPS: {'✅' if session.get(gps_url).status_code == 200 else '❌'}")
    
    return True

if __name__ == "__main__":
    try:
        test_apis()
    except KeyboardInterrupt:
        print("\n❌ Prueba cancelada")
    except Exception as e:
        print(f"\n❌ Error: {e}")
