/**
 * Service Worker para EURO SECURITY
 * Rastreo GPS automático en segundo plano
 * Funcionamiento offline y sincronización
 */

const CACHE_NAME = 'euro-security-v1.0.0';
const GPS_SYNC_TAG = 'gps-background-sync';
const GPS_TRACKING_INTERVAL = 30000; // 30 segundos
const OFFLINE_STORAGE_KEY = 'euro-security-offline-gps';

// Archivos para cachear (funcionamiento offline)
const CACHE_URLS = [
    '/',
    '/asistencia/marcar/',
    '/asistencia/mi-asistencia/',
    '/asistencia/dashboard/',
    '/static/manifest.json',
    '/static/css/bootstrap.min.css',
    '/static/js/bootstrap.bundle.min.js',
    // Agregar más recursos según necesidad
];

// Variables globales del Service Worker
let gpsTrackingActive = false;
let gpsTrackingInterval = null;
let lastKnownPosition = null;

/**
 * INSTALACIÓN DEL SERVICE WORKER
 */
self.addEventListener('install', event => {
    console.log('🔧 EURO SECURITY SW: Instalando...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('📦 Cacheando recursos offline');
                return cache.addAll(CACHE_URLS);
            })
            .then(() => {
                console.log('✅ Service Worker instalado correctamente');
                return self.skipWaiting();
            })
    );
});

/**
 * ACTIVACIÓN DEL SERVICE WORKER
 */
self.addEventListener('activate', event => {
    console.log('🚀 EURO SECURITY SW: Activando...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('🗑️ Eliminando cache antiguo:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker activado');
                return self.clients.claim();
            })
    );
});

/**
 * INTERCEPTAR REQUESTS (FUNCIONAMIENTO OFFLINE)
 */
self.addEventListener('fetch', event => {
    // Solo interceptar requests GET
    if (event.request.method !== 'GET') {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Devolver desde cache si existe
                if (response) {
                    return response;
                }
                
                // Sino, hacer request normal
                return fetch(event.request)
                    .then(response => {
                        // Cachear respuestas exitosas
                        if (response.status === 200) {
                            const responseClone = response.clone();
                            caches.open(CACHE_NAME)
                                .then(cache => {
                                    cache.put(event.request, responseClone);
                                });
                        }
                        return response;
                    })
                    .catch(() => {
                        // Si falla, mostrar página offline
                        return new Response(
                            '<h1>Sin conexión</h1><p>EURO SECURITY funcionará cuando recuperes la conexión.</p>',
                            { headers: { 'Content-Type': 'text/html' } }
                        );
                    });
            })
    );
});

/**
 * BACKGROUND SYNC - SINCRONIZACIÓN EN SEGUNDO PLANO
 */
self.addEventListener('sync', event => {
    console.log('🔄 Background Sync:', event.tag);
    
    if (event.tag === GPS_SYNC_TAG) {
        event.waitUntil(syncOfflineGPSData());
    }
});

/**
 * MENSAJES DESDE LA APLICACIÓN PRINCIPAL
 */
self.addEventListener('message', event => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'START_GPS_TRACKING':
            startGPSTracking(data);
            break;
            
        case 'STOP_GPS_TRACKING':
            stopGPSTracking();
            break;
            
        case 'UPDATE_GPS_CONFIG':
            updateGPSConfig(data);
            break;
            
        case 'GET_GPS_STATUS':
            event.ports[0].postMessage({
                active: gpsTrackingActive,
                lastPosition: lastKnownPosition
            });
            break;
    }
});

/**
 * INICIAR RASTREO GPS AUTOMÁTICO
 */
function startGPSTracking(config = {}) {
    console.log('🛰️ Iniciando rastreo GPS automático');
    
    if (gpsTrackingActive) {
        console.log('⚠️ GPS tracking ya está activo');
        return;
    }
    
    gpsTrackingActive = true;
    
    // Configuración del rastreo
    const trackingConfig = {
        interval: config.interval || GPS_TRACKING_INTERVAL,
        highAccuracy: config.highAccuracy !== false,
        timeout: config.timeout || 10000,
        maximumAge: config.maximumAge || 60000
    };
    
    // Iniciar rastreo periódico
    gpsTrackingInterval = setInterval(() => {
        captureGPSLocation(trackingConfig);
    }, trackingConfig.interval);
    
    // Capturar ubicación inicial
    captureGPSLocation(trackingConfig);
    
    // Notificar a la aplicación
    notifyClients('GPS_TRACKING_STARTED', { config: trackingConfig });
}

/**
 * DETENER RASTREO GPS
 */
function stopGPSTracking() {
    console.log('🛑 Deteniendo rastreo GPS');
    
    gpsTrackingActive = false;
    
    if (gpsTrackingInterval) {
        clearInterval(gpsTrackingInterval);
        gpsTrackingInterval = null;
    }
    
    notifyClients('GPS_TRACKING_STOPPED');
}

/**
 * CAPTURAR UBICACIÓN GPS
 */
function captureGPSLocation(config) {
    if (!gpsTrackingActive) return;
    
    // Usar la API de geolocalización
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(
            position => {
                const gpsData = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    altitude: position.coords.altitude,
                    timestamp: new Date().toISOString(),
                    tracking_type: 'AUTO',
                    battery_level: getBatteryLevel(),
                    device_info: getDeviceInfo()
                };
                
                lastKnownPosition = gpsData;
                console.log('📍 GPS capturado:', gpsData.latitude, gpsData.longitude);
                
                // Enviar al servidor
                sendGPSToServer(gpsData);
                
                // Notificar a la aplicación
                notifyClients('GPS_LOCATION_UPDATED', gpsData);
            },
            error => {
                console.error('❌ Error GPS:', error.message);
                handleGPSError(error);
            },
            {
                enableHighAccuracy: config.highAccuracy,
                timeout: config.timeout,
                maximumAge: config.maximumAge
            }
        );
    } else {
        console.error('❌ Geolocalización no soportada');
    }
}

/**
 * ENVIAR GPS AL SERVIDOR
 */
function sendGPSToServer(gpsData) {
    fetch('/asistencia/api/actualizar-gps/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(gpsData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ GPS enviado al servidor');
            
            // Verificar alertas
            if (data.alert_generated) {
                showNotification('⚠️ Alerta de Ubicación', {
                    body: 'Te encuentras fuera de tu área de trabajo asignada',
                    icon: '/static/icons/icon-192x192.png',
                    badge: '/static/icons/badge-72x72.png',
                    tag: 'location-alert'
                });
            }
        } else {
            console.error('❌ Error enviando GPS:', data.error);
        }
    })
    .catch(error => {
        console.error('❌ Error de red GPS:', error);
        // Guardar offline para sincronizar después
        storeGPSOffline(gpsData);
    });
}

/**
 * ALMACENAR GPS OFFLINE
 */
function storeGPSOffline(gpsData) {
    return new Promise((resolve, reject) => {
        // Usar IndexedDB para almacenamiento offline
        const request = indexedDB.open('EuroSecurityDB', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['gps_offline'], 'readwrite');
            const store = transaction.objectStore('gps_offline');
            
            store.add({
                ...gpsData,
                stored_at: new Date().toISOString()
            });
            
            transaction.oncomplete = () => {
                console.log('💾 GPS guardado offline');
                resolve();
            };
        };
        
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains('gps_offline')) {
                db.createObjectStore('gps_offline', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}

/**
 * SINCRONIZAR DATOS GPS OFFLINE
 */
async function syncOfflineGPSData() {
    console.log('🔄 Sincronizando datos GPS offline');
    
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('EuroSecurityDB', 1);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['gps_offline'], 'readwrite');
            const store = transaction.objectStore('gps_offline');
            
            store.getAll().onsuccess = async (event) => {
                const offlineData = event.target.result;
                
                if (offlineData.length === 0) {
                    resolve();
                    return;
                }
                
                console.log(`📤 Sincronizando ${offlineData.length} ubicaciones offline`);
                
                // Enviar cada ubicación al servidor
                for (const gpsData of offlineData) {
                    try {
                        await sendGPSToServerSync(gpsData);
                        // Eliminar del almacenamiento offline
                        store.delete(gpsData.id);
                    } catch (error) {
                        console.error('❌ Error sincronizando GPS:', error);
                    }
                }
                
                resolve();
            };
        };
        
        request.onerror = () => reject(request.error);
    });
}

/**
 * ENVIAR GPS AL SERVIDOR (SINCRONIZACIÓN)
 */
function sendGPSToServerSync(gpsData) {
    return fetch('/asistencia/api/actualizar-gps/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(gpsData)
    }).then(response => response.json());
}

/**
 * MOSTRAR NOTIFICACIÓN
 */
function showNotification(title, options = {}) {
    if ('Notification' in self && Notification.permission === 'granted') {
        return self.registration.showNotification(title, {
            icon: '/static/icons/icon-192x192.png',
            badge: '/static/icons/badge-72x72.png',
            vibrate: [200, 100, 200],
            requireInteraction: true,
            ...options
        });
    }
}

/**
 * NOTIFICAR A CLIENTES
 */
function notifyClients(type, data = {}) {
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({ type, data });
        });
    });
}

/**
 * OBTENER NIVEL DE BATERÍA
 */
function getBatteryLevel() {
    // Esta función se puede expandir con la Battery API
    return null; // Por ahora null, se puede implementar después
}

/**
 * OBTENER INFORMACIÓN DEL DISPOSITIVO
 */
function getDeviceInfo() {
    return `PWA - ${navigator.userAgent.split(' ')[0]}`;
}

/**
 * OBTENER CSRF TOKEN
 */
function getCSRFToken() {
    // Implementar según tu sistema de CSRF
    return 'dummy-token'; // Reemplazar con token real
}

/**
 * MANEJAR ERRORES GPS
 */
function handleGPSError(error) {
    let message = '';
    
    switch (error.code) {
        case error.PERMISSION_DENIED:
            message = 'Permisos de ubicación denegados';
            break;
        case error.POSITION_UNAVAILABLE:
            message = 'Ubicación no disponible';
            break;
        case error.TIMEOUT:
            message = 'Timeout obteniendo ubicación';
            break;
        default:
            message = 'Error desconocido de GPS';
    }
    
    console.error('❌ GPS Error:', message);
    notifyClients('GPS_ERROR', { message, code: error.code });
}

console.log('🚀 EURO SECURITY Service Worker cargado correctamente');
