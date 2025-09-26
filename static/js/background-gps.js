/**
 * Sistema de GPS en segundo plano para EURO SECURITY
 * Envía ubicación automáticamente cada 30 segundos
 */

class BackgroundGPS {
    constructor() {
        this.isActive = false;
        this.intervalId = null;
        this.lastPosition = null;
        this.sendInterval = 30000; // 30 segundos
        this.maxRetries = 3;
        this.currentRetries = 0;
        
        this.init();
    }
    
    async init() {
        console.log('📍 Inicializando GPS en segundo plano');
        
        // Verificar si el usuario está logueado
        if (!this.isUserLoggedIn()) {
            console.log('❌ Usuario no logueado, GPS deshabilitado');
            return;
        }
        
        // Solicitar permisos
        await this.requestPermissions();
        
        // Iniciar rastreo automático
        this.startBackgroundTracking();
        
        // Configurar eventos de visibilidad
        this.setupVisibilityHandlers();
    }
    
    isUserLoggedIn() {
        // Verificar si hay indicador de usuario autenticado
        return document.querySelector('[data-user-authenticated="true"]') !== null;
    }
    
    async requestPermissions() {
        try {
            // Solicitar permiso de geolocalización
            const permission = await navigator.permissions.query({name: 'geolocation'});
            
            if (permission.state === 'granted') {
                console.log('✅ Permisos de geolocalización concedidos');
                return true;
            } else if (permission.state === 'prompt') {
                // Solicitar permiso
                return new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        () => {
                            console.log('✅ Permisos de geolocalización concedidos');
                            resolve(true);
                        },
                        (error) => {
                            console.log('❌ Permisos de geolocalización denegados:', error);
                            resolve(false);
                        },
                        { timeout: 10000 }
                    );
                });
            } else {
                console.log('❌ Permisos de geolocalización denegados');
                return false;
            }
        } catch (error) {
            console.error('❌ Error solicitando permisos:', error);
            return false;
        }
    }
    
    startBackgroundTracking() {
        if (this.isActive) {
            console.log('⚠️ GPS ya está activo');
            return;
        }
        
        console.log('🟢 Iniciando rastreo GPS en segundo plano');
        this.isActive = true;
        
        // Enviar ubicación inmediatamente
        this.sendCurrentLocation();
        
        // Configurar intervalo
        this.intervalId = setInterval(() => {
            this.sendCurrentLocation();
        }, this.sendInterval);
        
        // Actualizar UI
        this.updateGPSStatus('active');
    }
    
    stopBackgroundTracking() {
        if (!this.isActive) {
            return;
        }
        
        console.log('🔴 Deteniendo rastreo GPS');
        this.isActive = false;
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        // Actualizar UI
        this.updateGPSStatus('inactive');
    }
    
    async sendCurrentLocation() {
        try {
            const position = await this.getCurrentPosition();
            
            if (!position) {
                console.log('❌ No se pudo obtener ubicación');
                this.handleError();
                return;
            }
            
            // Verificar si la posición cambió significativamente
            if (this.lastPosition && this.calculateDistance(this.lastPosition, position) < 10) {
                console.log('📍 Posición sin cambios significativos, omitiendo envío');
                return;
            }
            
            // Enviar al servidor
            const success = await this.sendLocationToServer(position);
            
            if (success) {
                this.lastPosition = position;
                this.currentRetries = 0;
                console.log('✅ Ubicación enviada exitosamente');
                this.updateGPSStatus('active', `Última actualización: ${new Date().toLocaleTimeString()}`);
            } else {
                this.handleError();
            }
            
        } catch (error) {
            console.error('❌ Error enviando ubicación:', error);
            this.handleError();
        }
    }
    
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocalización no soportada'));
                return;
            }
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy,
                        timestamp: new Date().toISOString()
                    });
                },
                (error) => {
                    console.error('Error obteniendo posición:', error);
                    resolve(null);
                },
                {
                    enableHighAccuracy: false, // Usar GPS de baja precisión para ahorrar batería
                    timeout: 15000,
                    maximumAge: 60000 // Aceptar posiciones de hasta 1 minuto
                }
            );
        });
    }
    
    async sendLocationToServer(position) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                             document.querySelector('meta[name="csrf-token"]')?.content;
            
            const response = await fetch('/asistencia/actualizar-gps/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    latitude: position.latitude,
                    longitude: position.longitude,
                    accuracy: position.accuracy,
                    timestamp: position.timestamp,
                    source: 'background_tracking'
                })
            });
            
            return response.ok;
            
        } catch (error) {
            console.error('❌ Error enviando al servidor:', error);
            return false;
        }
    }
    
    calculateDistance(pos1, pos2) {
        const R = 6371000; // Radio de la Tierra en metros
        const dLat = (pos2.latitude - pos1.latitude) * Math.PI / 180;
        const dLon = (pos2.longitude - pos1.longitude) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(pos1.latitude * Math.PI / 180) * Math.cos(pos2.latitude * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    handleError() {
        this.currentRetries++;
        
        if (this.currentRetries >= this.maxRetries) {
            console.log('❌ Máximo de reintentos alcanzado, pausando GPS');
            this.updateGPSStatus('error', 'Error de conexión');
            
            // Reintentar después de 5 minutos
            setTimeout(() => {
                this.currentRetries = 0;
                console.log('🔄 Reintentando GPS después de pausa');
            }, 300000);
        }
    }
    
    updateGPSStatus(status, message = '') {
        const statusElement = document.getElementById('gps-status');
        const messageElement = document.getElementById('gps-status-message');
        
        if (statusElement) {
            switch (status) {
                case 'active':
                    statusElement.className = 'badge bg-success me-2';
                    statusElement.textContent = 'GPS Activo';
                    break;
                case 'inactive':
                    statusElement.className = 'badge bg-secondary me-2';
                    statusElement.textContent = 'GPS Inactivo';
                    break;
                case 'error':
                    statusElement.className = 'badge bg-danger me-2';
                    statusElement.textContent = 'GPS Error';
                    break;
            }
        }
        
        if (messageElement && message) {
            messageElement.textContent = message;
            messageElement.style.display = 'block';
        }
    }
    
    setupVisibilityHandlers() {
        // Continuar GPS incluso cuando la app está en segundo plano
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                console.log('📱 App en segundo plano, GPS continúa activo');
            } else {
                console.log('📱 App en primer plano');
                // Enviar ubicación inmediatamente al volver
                if (this.isActive) {
                    this.sendCurrentLocation();
                }
            }
        });
        
        // Manejar eventos de pausa/reanudación
        window.addEventListener('beforeunload', () => {
            console.log('📱 App cerrándose, manteniendo GPS activo');
        });
    }
    
    // Método público para toggle manual
    toggleGPS() {
        if (this.isActive) {
            this.stopBackgroundTracking();
        } else {
            this.startBackgroundTracking();
        }
    }
}

// Inicializar GPS en segundo plano cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.backgroundGPS = new BackgroundGPS();
    
    // Conectar botón de toggle si existe
    const toggleButton = document.getElementById('gps-toggle-btn');
    if (toggleButton) {
        toggleButton.addEventListener('click', () => {
            window.backgroundGPS.toggleGPS();
        });
    }
});

// Exportar para uso global
window.BackgroundGPS = BackgroundGPS;
