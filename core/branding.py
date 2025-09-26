"""
Configuración de branding y assets de EURO SECURITY
"""
from django.conf import settings
import os

class EuroSecurityBranding:
    """Configuración centralizada de branding para EURO SECURITY"""
    
    # Información de la empresa
    COMPANY_NAME = "EURO SECURITY"
    COMPANY_TAGLINE = "Seguridad Física Profesional"
    COMPANY_DESCRIPTION = "Soluciones integrales de seguridad y control de personal"
    
    # Colores corporativos
    COLORS = {
        'primary': '#1e40af',      # Azul principal
        'secondary': '#7c3aed',    # Púrpura
        'success': '#059669',      # Verde
        'warning': '#d97706',      # Naranja
        'danger': '#dc2626',       # Rojo
        'dark': '#1f2937',         # Gris oscuro
        'light': '#f8fafc',        # Gris claro
    }
    
    # Gradientes
    GRADIENTS = {
        'primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'success': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        'warning': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        'info': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    }
    
    # Rutas de logos (relativas a STATIC_URL)
    LOGOS = {
        'main': 'images/logos/euro-security-logo.png',
        'icon': 'images/logos/euro-security-icon.jpg',
        'white': 'images/logos/euro-security-white.png',
        'favicon': 'images/logos/favicon.ico',
        'business_card': 'images/branding/business-card.jpg',
        'letterhead': 'images/branding/letterhead.jpg',
    }
    
    # Información de contacto
    CONTACT_INFO = {
        'phone': '+593 4 XXX-XXXX',
        'email': 'info@eurosecurity.ec',
        'address': 'Guayaquil, Ecuador',
        'website': 'www.eurosecurity.ec',
    }
    
    @classmethod
    def get_logo_url(cls, logo_type='main'):
        """Obtiene la URL completa de un logo"""
        logo_path = cls.LOGOS.get(logo_type, cls.LOGOS['main'])
        return f"{settings.STATIC_URL}{logo_path}"
    
    @classmethod
    def get_context(cls):
        """Obtiene el contexto completo de branding para templates"""
        return {
            'company_name': cls.COMPANY_NAME,
            'company_tagline': cls.COMPANY_TAGLINE,
            'company_description': cls.COMPANY_DESCRIPTION,
            'colors': cls.COLORS,
            'gradients': cls.GRADIENTS,
            'logos': {key: cls.get_logo_url(key) for key in cls.LOGOS.keys()},
            'contact': cls.CONTACT_INFO,
        }
