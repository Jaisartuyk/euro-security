"""
Custom Cloudinary Storage Backend
"""
from django.core.files.storage import Storage
from django.conf import settings
import cloudinary
import cloudinary.uploader
from urllib.parse import urlparse
import os


class CloudinaryStorage(Storage):
    """
    Custom storage backend for Cloudinary
    """
    
    def __init__(self):
        print("🔧 Inicializando CloudinaryStorage custom...")
        # Configurar cloudinary desde settings
        if hasattr(settings, 'CLOUDINARY_STORAGE'):
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
                api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
                api_secret=settings.CLOUDINARY_STORAGE['API_SECRET'],
                secure=settings.CLOUDINARY_STORAGE.get('SECURE', True)
            )
            print(f"✅ CloudinaryStorage configurado: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")
        else:
            print("❌ CLOUDINARY_STORAGE no encontrado en settings")
    
    def _save(self, name, content):
        """
        Guardar archivo en Cloudinary
        """
        print(f"📤 CloudinaryStorage._save() llamado para: {name}")
        try:
            # Subir a Cloudinary
            print(f"   Subiendo a Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                content,
                folder=os.path.dirname(name),
                public_id=os.path.splitext(os.path.basename(name))[0],
                resource_type='auto'
            )
            
            print(f"✅ Subido exitosamente: {upload_result['secure_url']}")
            # Retornar la URL pública
            return upload_result['secure_url']
        except Exception as e:
            print(f"❌ Error subiendo a Cloudinary: {e}")
            raise
    
    def url(self, name):
        """
        Retornar URL del archivo
        """
        # Si ya es una URL completa, retornarla
        if name.startswith('http'):
            return name
        
        # Si no, construir URL de Cloudinary
        return f"https://res.cloudinary.com/{settings.CLOUDINARY_STORAGE['CLOUD_NAME']}/image/upload/{name}"
    
    def exists(self, name):
        """
        Verificar si el archivo existe
        """
        # Para Cloudinary, siempre retornar False para forzar subida
        return False
    
    def delete(self, name):
        """
        Eliminar archivo de Cloudinary
        """
        try:
            # Extraer public_id de la URL
            if name.startswith('http'):
                parsed = urlparse(name)
                path_parts = parsed.path.split('/')
                # Encontrar el public_id (después de /upload/)
                if 'upload' in path_parts:
                    upload_index = path_parts.index('upload')
                    public_id = '/'.join(path_parts[upload_index + 1:])
                    public_id = os.path.splitext(public_id)[0]  # Quitar extensión
                else:
                    public_id = name
            else:
                public_id = os.path.splitext(name)[0]
            
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            print(f"⚠️ Error eliminando de Cloudinary: {e}")
    
    def size(self, name):
        """
        Retornar tamaño del archivo
        """
        return 0  # No implementado
