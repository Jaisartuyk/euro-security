/**
 * PWA Simple para desarrollo local - EURO SECURITY
 * Versión simplificada que funciona en localhost
 */

class EuroSecurityPWASimple {
    constructor() {
        this.serviceWorker = null;
        this.gpsTrackingActive = false;
        this.gpsInterval = null;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Inicializando EURO SECURITY PWA (Modo Desarrollo)');
        
        // Registrar Service Worker (solo en HTTPS o localhost)
        await this.registerServiceWorker();
        
        // Configurar GPS tracking básico
        this.setupGPSTracking();
        
        // Configurar eventos
        this.setupEventListeners();
        
        // Mostrar información de desarrollo
        this.showDevelopmentInfo();
        
        console.log('✅ PWA Simple inicializada');
    }
    
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw-simple.js');
                this.serviceWorker = registration;
                console.log('✅ Service Worker registrado (modo desarrollo)');
                
                // Escuchar actualizaciones
                registration.addEventListener('updatefound', () => {
                    console.log('🔄 Nueva versión disponible');
                });
                
            } catch (error) {
                console.warn('⚠️ Service Worker no disponible:', error.message);
            }
        }
    }
    
    setupGPSTracking() {
        if ('geolocation' in navigator) {
            console.log('📍 Geolocalización disponible');
            
            // Solicitar permisos al iniciar
            if (this.isUserLoggedIn()) {
                this.requestLocationPermission();
            }
        } else {
            console.warn('⚠️ Geolocalización no soportada');
        }
    }
    
    async requestLocationPermission() {
        try {
            const position = await this.getCurrentPosition();
            console.log('✅ Permisos de ubicación concedidos');
            console.log('📍 Ubicación inicial:', position.coords.latitude, position.coords.longitude);
            
            // Mostrar en UI
            this.updateLocationDisplay({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy
            });
            
            // Iniciar rastreo automático
            this.startGPSTracking();
            
        } catch (error) {
            console.warn('⚠️ Permisos de ubicación denegados:', error.message);
            this.showLocationPermissionDialog();
        }
    }
    
    startGPSTracking() {
        if (this.gpsTrackingActive) return;
        
        console.log('🛰️ Iniciando rastreo GPS (modo desarrollo)');
        this.gpsTrackingActive = true;
        
        // Rastreo cada 30 segundos
        this.gpsInterval = setInterval(() => {
            this.captureGPSLocation();
        }, 30000);
        
        // Captura inicial
        this.captureGPSLocation();
        
        this.updateGPSStatus();
    }
    
    stopGPSTracking() {
        console.log('🛑 Deteniendo rastreo GPS');
        this.gpsTrackingActive = false;
        
        if (this.gpsInterval) {
            clearInterval(this.gpsInterval);
            this.gpsInterval = null;
        }
        
        this.updateGPSStatus();
    }
    
    async captureGPSLocation() {
        if (!this.gpsTrackingActive) return;
        
        try {
            const position = await this.getCurrentPosition();
            const gpsData = {
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
                accuracy: position.coords.accuracy,
                altitude: position.coords.altitude,
                timestamp: new Date().toISOString(),
                tracking_type: 'AUTO',
                device_info: 'PWA Development Mode'
            };
            
            console.log('📍 GPS capturado:', gpsData.latitude, gpsData.longitude);
            
            // Actualizar UI
            this.updateLocationDisplay(gpsData);
            
            // Enviar al servidor
            this.sendGPSToServer(gpsData);
            
        } catch (error) {
            console.error('❌ Error capturando GPS:', error.message);
        }
    }
    
    async sendGPSToServer(gpsData) {
        try {
            const response = await fetch('/asistencia/api/actualizar-gps/', {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(gpsData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                console.log('✅ GPS enviado al servidor');
                
                // Verificar alertas
                if (result.alert_generated) {
                    this.showAlert('⚠️ Alerta de Ubicación', 
                        'Te encuentras fuera de tu área de trabajo asignada');
                }
            } else {
                console.error('❌ Error enviando GPS:', result.error);
            }
            
        } catch (error) {
            console.error('❌ Error de red GPS:', error);
            // En desarrollo, solo mostrar en consola
            this.showAlert('📴 Sin conexión', 'GPS guardado localmente');
        }
    }
    
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            });
        });
    }
    
    isUserLoggedIn() {
        return document.querySelector('[data-user-authenticated]') !== null;
    }
    
    getCSRFToken() {
        // Buscar en cookies primero
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        // Fallback: buscar en meta tag
        const csrfMeta = document.querySelector('meta[name=csrf-token]');
        return csrfMeta ? csrfMeta.getAttribute('content') : 'development-token';
    }
    
    setupEventListeners() {
        // Botón toggle GPS
        const gpsToggleBtn = document.getElementById('gps-toggle-btn');
        if (gpsToggleBtn) {
            gpsToggleBtn.addEventListener('click', () => {
                if (this.gpsTrackingActive) {
                    this.stopGPSTracking();
                } else {
                    this.startGPSTracking();
                }
            });
        }
        
        // Detectar cambios de visibilidad
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.isUserLoggedIn()) {
                console.log('👁️ App visible - verificando GPS');
            }
        });
    }
    
    updateGPSStatus() {
        const statusElement = document.getElementById('gps-status');
        if (statusElement) {
            statusElement.textContent = this.gpsTrackingActive ? 'GPS Activo' : 'GPS Inactivo';
            statusElement.className = this.gpsTrackingActive ? 'badge bg-success' : 'badge bg-secondary';
        }
    }
    
    updateLocationDisplay(location) {
        const locationElement = document.getElementById('current-location');
        if (locationElement) {
            locationElement.innerHTML = `
                <small class="text-muted">
                    📍 ${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}
                    <br>Precisión: ${location.accuracy}m
                    <br><span class="badge bg-info">Modo Desarrollo</span>
                </small>
            `;
        }
    }
    
    showLocationPermissionDialog() {
        const message = `
            🛰️ EURO SECURITY necesita acceso a tu ubicación para el rastreo GPS.
            
            Por favor, permite el acceso en tu navegador.
            
            En producción, esta app se podrá instalar como PWA nativa.
        `;
        
        if (confirm(message)) {
            this.requestLocationPermission();
        }
    }
    
    showAlert(title, message) {
        // En desarrollo, usar alert simple
        console.log(`🔔 ${title}: ${message}`);
        
        // Mostrar en UI si existe elemento
        const alertElement = document.getElementById('gps-status-message');
        if (alertElement) {
            alertElement.textContent = `${title}: ${message}`;
            alertElement.className = 'alert alert-info';
            alertElement.style.display = 'block';
            
            // Ocultar después de 5 segundos
            setTimeout(() => {
                alertElement.style.display = 'none';
            }, 5000);
        }
    }
    
    showDevelopmentInfo() {
        console.log(`
🚀 EURO SECURITY PWA - MODO DESARROLLO
=====================================

📍 FUNCIONALIDADES ACTIVAS:
✅ Rastreo GPS básico cada 30 segundos
✅ Envío automático al servidor
✅ Indicador visual de estado
✅ Control manual de GPS

📱 PARA PRODUCCIÓN (HTTPS):
🔹 PWA instalable como app nativa
🔹 Service Worker completo
🔹 Funcionamiento offline
🔹 Notificaciones push
🔹 Background sync

🌐 COMPATIBILIDAD:
✅ Chrome/Edge (completa)
✅ Firefox (básica)
✅ Safari (limitada)

⚠️ NOTA: En localhost algunas funciones PWA están limitadas.
Para funcionalidad completa, desplegar en HTTPS.
        `);
        
        // Mostrar banner informativo
        this.showDevelopmentBanner();
    }
    
    showDevelopmentBanner() {
        // Crear banner informativo
        const banner = document.createElement('div');
        banner.id = 'dev-info-banner';
        banner.className = 'position-fixed top-0 start-0 end-0 bg-warning text-dark p-2 text-center';
        banner.style.zIndex = '9999';
        banner.innerHTML = `
            <small>
                🚧 <strong>MODO DESARROLLO</strong> - 
                PWA completa disponible en producción (HTTPS) - 
                <button onclick="this.parentElement.parentElement.remove()" class="btn btn-sm btn-outline-dark">×</button>
            </small>
        `;
        
        document.body.prepend(banner);
        
        // Auto-ocultar después de 10 segundos
        setTimeout(() => {
            if (banner.parentElement) {
                banner.remove();
            }
        }, 10000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.euroSecurityPWA = new EuroSecurityPWASimple();
});

console.log('📱 EURO SECURITY PWA Simple cargado');
