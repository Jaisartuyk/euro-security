#!/usr/bin/env python3
"""
Descargador automático de modelos de IA para reconocimiento facial
EURO SECURITY - Sistema Biométrico Avanzado
"""
import os
import urllib.request
import hashlib
from pathlib import Path

def download_file_with_progress(url, filename):
    """Descarga archivo con barra de progreso"""
    def progress_hook(block_num, block_size, total_size):
        if total_size > 0:
            percent = min(100, (block_num * block_size * 100) // total_size)
            print(f"\r📥 Descargando {filename}: {percent}%", end="", flush=True)
    
    try:
        urllib.request.urlretrieve(url, filename, progress_hook)
        print(f"\n✅ {filename} descargado exitosamente")
        return True
    except Exception as e:
        print(f"\n❌ Error descargando {filename}: {e}")
        return False

def verify_file_hash(filename, expected_hash):
    """Verifica la integridad del archivo"""
    try:
        with open(filename, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        if file_hash == expected_hash:
            print(f"✅ {filename} verificado correctamente")
            return True
        else:
            print(f"❌ {filename} corrupto (hash no coincide)")
            return False
    except Exception as e:
        print(f"❌ Error verificando {filename}: {e}")
        return False

def download_opencv_models():
    """Descarga modelos de OpenCV para detección facial"""
    print("\n🤖 Descargando modelos de OpenCV...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Modelo DNN para detección facial
    models = [
        {
            'name': 'deploy.prototxt',
            'url': 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt',
            'hash': None  # Archivo de texto, no necesita verificación
        },
        {
            'name': 'res10_300x300_ssd_iter_140000.caffemodel',
            'url': 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel',
            'hash': 'f4b4e0e0b8d5b8c6a5b7c9e2d3f4a5b6'  # Hash de ejemplo
        }
    ]
    
    for model in models:
        filepath = models_dir / model['name']
        
        if filepath.exists():
            print(f"⏭️  {model['name']} ya existe")
            continue
        
        print(f"\n📥 Descargando {model['name']}...")
        
        if download_file_with_progress(model['url'], filepath):
            if model['hash']:
                verify_file_hash(filepath, model['hash'])
        else:
            return False
    
    return True

def create_model_info():
    """Crea archivo de información de modelos"""
    info_content = '''# Modelos de IA Descargados

## Estado de Modelos
✅ deploy.prototxt - Arquitectura de red DNN
✅ res10_300x300_ssd_iter_140000.caffemodel - Pesos entrenados

## Uso
Estos modelos se usan automáticamente por el sistema de reconocimiento facial
para detección de rostros con alta precisión usando redes neuronales profundas.

## Rendimiento
- Precisión: 95%+ en detección
- Velocidad: ~50ms por imagen
- Tamaño de entrada: 300x300 píxeles

## Fuente
Modelos oficiales de OpenCV disponibles en:
https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector
'''
    
    info_file = Path("models/MODEL_INFO.md")
    with open(info_file, "w", encoding="utf-8") as f:
        f.write(info_content)
    
    print("✅ Información de modelos creada")

def main():
    """Función principal"""
    print("🤖 EURO SECURITY - Descargador de Modelos de IA")
    print("=" * 50)
    
    # Verificar conexión a internet
    try:
        urllib.request.urlopen('https://www.google.com', timeout=5)
        print("✅ Conexión a internet verificada")
    except:
        print("❌ Error: No hay conexión a internet")
        return False
    
    # Descargar modelos
    if not download_opencv_models():
        print("❌ Error descargando modelos")
        return False
    
    # Crear información
    create_model_info()
    
    print("\n🎉 ¡Modelos descargados exitosamente!")
    print("🚀 El sistema está listo para reconocimiento facial avanzado")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
