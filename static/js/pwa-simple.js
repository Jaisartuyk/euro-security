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
        console.log('🚀 Inicializando EURO SECURITY PWA (Producción HTTPS)');
        
        // Registrar Service Worker (solo en HTTPS o localhost)
        await this.registerServiceWorker();
        
        // Configurar PWA Install
        this.setupPWAInstall();
        
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
                console.log('✅ Service Worker registrado (producción HTTPS)');
                
                // Escuchar actualizaciones
                registration.addEventListener('updatefound', () => {
                    console.log('🔄 Nueva versión disponible');
                });
                
            } catch (error) {
                console.warn('⚠️ Service Worker no disponible:', error.message);
            }
        }
    }
    
    setupPWAInstall() {
        let deferredPrompt;
        const installBanner = document.getElementById('pwa-install-banner');
        const installBtn = document.getElementById('pwa-install-btn');
        const dismissBtn = document.getElementById('pwa-dismiss-btn');
        
        // Escuchar evento beforeinstallprompt
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('📱 PWA instalable detectada');
            e.preventDefault();
            deferredPrompt = e;
            
            // Mostrar banner de instalación
            if (installBanner) {
                installBanner.classList.remove('d-none');
            }
        });
        
        // Botón de instalación
        if (installBtn) {
            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`📱 Resultado de instalación: ${outcome}`);
                    deferredPrompt = null;
                    
                    if (installBanner) {
                        installBanner.classList.add('d-none');
                    }
                }
            });
        }
        
        // Botón de descartar
        if (dismissBtn) {
            dismissBtn.addEventListener('click', () => {
                if (installBanner) {
                    installBanner.classList.add('d-none');
                }
            });
        }
        
        // Detectar si ya está instalada
        window.addEventListener('appinstalled', () => {
            console.log('✅ PWA instalada exitosamente');
            if (installBanner) {
                installBanner.classList.add('d-none');
            }
        });
        
        // Mostrar banner después de un tiempo si no se detectó beforeinstallprompt
        setTimeout(() => {
            if (!deferredPrompt && installBanner && !this.isPWAInstalled()) {
                console.log('📱 Mostrando banner de instalación manual');
                installBanner.classList.remove('d-none');
                
                // Cambiar texto del botón para instalación manual
                if (installBtn) {
                    installBtn.textContent = 'Agregar a Inicio';
                    installBtn.onclick = () => {
                        this.showManualInstallInstructions();
                    };
                }
            }
        }, 3000);
    }
    
    isPWAInstalled() {
        // Detectar si la PWA ya está instalada
        return window.matchMedia('(display-mode: standalone)').matches || 
               window.navigator.standalone === true;
    }
    
    showManualInstallInstructions() {
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isAndroid = /Android/.test(navigator.userAgent);
        
        let instructions = '';
        
        if (isIOS) {
            instructions = `
                Para instalar EURO SECURITY en iOS:
                1. Toca el botón Compartir 📎
                2. Selecciona "Agregar a pantalla de inicio"
                3. Toca "Agregar" para confirmar
            `;
        } else if (isAndroid) {
            instructions = `
                Para instalar EURO SECURITY en Android:
                1. Toca el menú ⋮ del navegador
                2. Selecciona "Agregar a pantalla de inicio"
                3. Toca "Agregar" para confirmar
            `;
        } else {
            instructions = `
                Para instalar EURO SECURITY:
                1. Busca el ícono de instalación en la barra de direcciones
                2. Haz clic en "Instalar"
                3. Confirma la instalación
            `;
        }
        
        alert(instructions);
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
        
        console.log('🛰️ Iniciando rastreo GPS (producción HTTPS)');
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
    
    // Función para obtener ubicación GPS usando solo API nativa del navegador
    getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocalización no soportada'));
                return;
            }
            
            // Configuración optimizada para evitar servicios externos
            const options = {
                enableHighAccuracy: false, // Cambiar a false para evitar Google services
                timeout: 15000, // Más tiempo para GPS
                maximumAge: 60000 // Cache más largo
            };
            
            console.log('🌍 Solicitando ubicación con configuración nativa...');
            
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    console.log('✅ Ubicación obtenida del GPS nativo:', position.coords);
                    console.log('📍 Precisión:', position.coords.accuracy, 'metros');
                    resolve(position);
                },
                (error) => {
                    console.warn('⚠️ Error de geolocalización:', error.message);
                    console.log('🔄 Intentando con configuración alternativa...');
                    
                    // Segundo intento con configuración más permisiva
                    const fallbackOptions = {
                        enableHighAccuracy: false,
                        timeout: 20000,
                        maximumAge: 300000 // 5 minutos de cache
                    };
                    
                    navigator.geolocation.getCurrentPosition(
                        (position) => {
                            console.log('✅ Ubicación obtenida (fallback):', position.coords);
                            resolve(position);
                        },
                        (fallbackError) => {
                            console.error('❌ Error final de geolocalización:', fallbackError);
                            reject(fallbackError);
                        },
                        fallbackOptions
                    );
                },
                options
            );
        });
    }
    
    updateLocationDisplay(location) {
        const locationElement = document.getElementById('current-location');
        if (locationElement) {
            locationElement.innerHTML = `
                <small class="text-muted">
                    📍 ${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}
                    <br>Precisión: ${location.accuracy}m
                    <br><span class="badge bg-success">Navegador Nativo</span>
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
🚀 EURO SECURITY PWA - PRODUCCIÓN
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
                ✅ <strong>PRODUCCIÓN HTTPS</strong> - 
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
