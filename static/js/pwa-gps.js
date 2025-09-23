/**
 * PWA GPS Manager para EURO SECURITY
 * Gestión de rastreo GPS automático y PWA
 */

class EuroSecurityPWA {
    constructor() {
        this.serviceWorker = null;
        this.gpsTrackingActive = false;
        this.installPrompt = null;
        this.notificationPermission = false;
        this.locationPermission = false;
        
        this.init();
    }
    
    /**
     * INICIALIZAR PWA
     */
    async init() {
        console.log('🚀 Inicializando EURO SECURITY PWA');
        
        // Registrar Service Worker
        await this.registerServiceWorker();
        
        // Configurar PWA
        this.setupPWAInstallation();
        this.setupNotifications();
        this.setupLocationPermissions();
        
        // Iniciar rastreo GPS automático si el usuario está logueado
        if (this.isUserLoggedIn()) {
            await this.startAutomaticGPSTracking();
        }
        
        // Configurar eventos
        this.setupEventListeners();
        
        console.log('✅ EURO SECURITY PWA inicializada');
    }
    
    /**
     * REGISTRAR SERVICE WORKER
     */
    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/static/sw.js');
                this.serviceWorker = registration;
                
                console.log('✅ Service Worker registrado:', registration.scope);
                
                // Escuchar mensajes del Service Worker
                navigator.serviceWorker.addEventListener('message', event => {
                    this.handleServiceWorkerMessage(event.data);
                });
                
                return registration;
            } catch (error) {
                console.error('❌ Error registrando Service Worker:', error);
            }
        } else {
            console.warn('⚠️ Service Worker no soportado');
        }
    }
    
    /**
     * CONFIGURAR INSTALACIÓN PWA
     */
    setupPWAInstallation() {
        // Capturar evento de instalación
        window.addEventListener('beforeinstallprompt', event => {
            event.preventDefault();
            this.installPrompt = event;
            this.showInstallButton();
        });
        
        // Detectar cuando se instala
        window.addEventListener('appinstalled', () => {
            console.log('🎉 PWA instalada correctamente');
            this.hideInstallButton();
            this.showWelcomeMessage();
        });
    }
    
    /**
     * CONFIGURAR NOTIFICACIONES
     */
    async setupNotifications() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            this.notificationPermission = permission === 'granted';
            
            if (this.notificationPermission) {
                console.log('✅ Permisos de notificación concedidos');
            } else {
                console.warn('⚠️ Permisos de notificación denegados');
            }
        }
    }
    
    /**
     * CONFIGURAR PERMISOS DE UBICACIÓN
     */
    async setupLocationPermissions() {
        if ('geolocation' in navigator) {
            try {
                // Solicitar permisos de ubicación
                const position = await this.getCurrentPosition();
                this.locationPermission = true;
                console.log('✅ Permisos de ubicación concedidos');
                
                // Mostrar ubicación inicial
                console.log('📍 Ubicación inicial:', position.coords.latitude, position.coords.longitude);
                
            } catch (error) {
                console.warn('⚠️ Permisos de ubicación denegados:', error.message);
                this.showLocationPermissionDialog();
            }
        }
    }
    
    /**
     * INICIAR RASTREO GPS AUTOMÁTICO
     */
    async startAutomaticGPSTracking() {
        if (!this.locationPermission) {
            console.warn('⚠️ No hay permisos de ubicación para rastreo GPS');
            return;
        }
        
        if (!this.serviceWorker) {
            console.warn('⚠️ Service Worker no disponible para rastreo GPS');
            return;
        }
        
        console.log('🛰️ Iniciando rastreo GPS automático');
        
        // Configuración del rastreo
        const trackingConfig = {
            interval: 30000, // 30 segundos
            highAccuracy: true,
            timeout: 10000,
            maximumAge: 60000
        };
        
        // Enviar mensaje al Service Worker
        this.sendMessageToServiceWorker('START_GPS_TRACKING', trackingConfig);
        
        this.gpsTrackingActive = true;
        this.updateGPSStatus();
        
        // Mostrar notificación de inicio
        if (this.notificationPermission) {
            new Notification('🛰️ EURO SECURITY', {
                body: 'Rastreo GPS automático iniciado',
                icon: '/static/icons/icon-192x192.png'
            });
        }
    }
    
    /**
     * DETENER RASTREO GPS
     */
    stopGPSTracking() {
        console.log('🛑 Deteniendo rastreo GPS');
        
        this.sendMessageToServiceWorker('STOP_GPS_TRACKING');
        this.gpsTrackingActive = false;
        this.updateGPSStatus();
    }
    
    /**
     * INSTALAR PWA
     */
    async installPWA() {
        if (this.installPrompt) {
            this.installPrompt.prompt();
            const result = await this.installPrompt.userChoice;
            
            if (result.outcome === 'accepted') {
                console.log('✅ Usuario aceptó instalar PWA');
            } else {
                console.log('❌ Usuario rechazó instalar PWA');
            }
            
            this.installPrompt = null;
        }
    }
    
    /**
     * ENVIAR MENSAJE AL SERVICE WORKER
     */
    sendMessageToServiceWorker(type, data = {}) {
        if (navigator.serviceWorker.controller) {
            navigator.serviceWorker.controller.postMessage({ type, data });
        }
    }
    
    /**
     * MANEJAR MENSAJES DEL SERVICE WORKER
     */
    handleServiceWorkerMessage(message) {
        const { type, data } = message;
        
        switch (type) {
            case 'GPS_TRACKING_STARTED':
                console.log('✅ Rastreo GPS iniciado en Service Worker');
                this.onGPSTrackingStarted(data);
                break;
                
            case 'GPS_TRACKING_STOPPED':
                console.log('🛑 Rastreo GPS detenido en Service Worker');
                this.onGPSTrackingStopped();
                break;
                
            case 'GPS_LOCATION_UPDATED':
                console.log('📍 Ubicación GPS actualizada:', data);
                this.onGPSLocationUpdated(data);
                break;
                
            case 'GPS_ERROR':
                console.error('❌ Error GPS:', data.message);
                this.onGPSError(data);
                break;
        }
    }
    
    /**
     * OBTENER POSICIÓN ACTUAL
     */
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            });
        });
    }
    
    /**
     * VERIFICAR SI EL USUARIO ESTÁ LOGUEADO
     */
    isUserLoggedIn() {
        // Verificar si hay elementos que indican usuario logueado
        return document.querySelector('[data-user-authenticated]') !== null ||
               document.body.classList.contains('authenticated') ||
               localStorage.getItem('user_authenticated') === 'true';
    }
    
    /**
     * CONFIGURAR EVENT LISTENERS
     */
    setupEventListeners() {
        // Botón de instalación PWA
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.addEventListener('click', () => this.installPWA());
        }
        
        // Botón de toggle GPS
        const gpsToggleBtn = document.getElementById('gps-toggle-btn');
        if (gpsToggleBtn) {
            gpsToggleBtn.addEventListener('click', () => {
                if (this.gpsTrackingActive) {
                    this.stopGPSTracking();
                } else {
                    this.startAutomaticGPSTracking();
                }
            });
        }
        
        // Detectar cuando la app vuelve al primer plano
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.isUserLoggedIn()) {
                // Reactivar rastreo si es necesario
                this.checkGPSStatus();
            }
        });
        
        // Detectar cambios de conexión
        window.addEventListener('online', () => {
            console.log('🌐 Conexión restaurada');
            this.onConnectionRestored();
        });
        
        window.addEventListener('offline', () => {
            console.log('📴 Sin conexión - modo offline');
            this.onConnectionLost();
        });
    }
    
    /**
     * CALLBACKS DE EVENTOS GPS
     */
    onGPSTrackingStarted(config) {
        this.showGPSStatus('Rastreo GPS activo', 'success');
    }
    
    onGPSTrackingStopped() {
        this.showGPSStatus('Rastreo GPS detenido', 'warning');
    }
    
    onGPSLocationUpdated(location) {
        this.updateLocationDisplay(location);
        this.checkLocationAlerts(location);
    }
    
    onGPSError(error) {
        this.showGPSStatus(`Error GPS: ${error.message}`, 'danger');
    }
    
    onConnectionRestored() {
        // Sincronizar datos offline
        if (this.serviceWorker && 'sync' in window.ServiceWorkerRegistration.prototype) {
            this.serviceWorker.sync.register('gps-background-sync');
        }
    }
    
    onConnectionLost() {
        this.showGPSStatus('Sin conexión - guardando offline', 'info');
    }
    
    /**
     * MÉTODOS DE UI
     */
    showInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
        }
    }
    
    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }
    
    showWelcomeMessage() {
        if (this.notificationPermission) {
            new Notification('🎉 ¡Bienvenido a EURO SECURITY!', {
                body: 'La aplicación se instaló correctamente y está lista para usar',
                icon: '/static/icons/icon-192x192.png'
            });
        }
    }
    
    showLocationPermissionDialog() {
        // Mostrar modal o mensaje pidiendo permisos de ubicación
        const message = `
            Para el rastreo GPS automático, necesitamos permisos de ubicación.
            Por favor, permite el acceso a tu ubicación en la configuración del navegador.
        `;
        
        if (confirm(message)) {
            // Intentar solicitar permisos nuevamente
            this.setupLocationPermissions();
        }
    }
    
    updateGPSStatus() {
        const statusElement = document.getElementById('gps-status');
        if (statusElement) {
            statusElement.textContent = this.gpsTrackingActive ? 'GPS Activo' : 'GPS Inactivo';
            statusElement.className = this.gpsTrackingActive ? 'badge bg-success' : 'badge bg-secondary';
        }
    }
    
    showGPSStatus(message, type = 'info') {
        console.log(`📱 GPS Status: ${message}`);
        
        // Mostrar en UI si existe elemento
        const statusElement = document.getElementById('gps-status-message');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `alert alert-${type}`;
        }
    }
    
    updateLocationDisplay(location) {
        const locationElement = document.getElementById('current-location');
        if (locationElement) {
            locationElement.innerHTML = `
                <small class="text-muted">
                    📍 ${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}
                    <br>Precisión: ${location.accuracy}m
                </small>
            `;
        }
    }
    
    checkLocationAlerts(location) {
        // Verificar si hay alertas de ubicación
        // Esta lógica se puede expandir según necesidades
    }
    
    checkGPSStatus() {
        // Verificar estado del GPS en el Service Worker
        this.sendMessageToServiceWorker('GET_GPS_STATUS');
    }
}

// Inicializar PWA cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.euroSecurityPWA = new EuroSecurityPWA();
});

// Exportar para uso global
window.EuroSecurityPWA = EuroSecurityPWA;
