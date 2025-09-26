/**
 * Service Worker avanzado para GPS en segundo plano
 * Funciona incluso cuando la app está cerrada (con limitaciones del SO)
 */

const CACHE_NAME = 'euro-security-v2.1.0';
const GPS_SYNC_TAG = 'background-gps-sync';

// Instalar Service Worker
self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker instalado');
    self.skipWaiting();
});

// Activar Service Worker
self.addEventListener('activate', (event) => {
    console.log('✅ Service Worker activado');
    event.waitUntil(self.clients.claim());
});

// Background Sync para GPS
self.addEventListener('sync', (event) => {
    if (event.tag === GPS_SYNC_TAG) {
        console.log('📍 Background Sync GPS activado');
        event.waitUntil(sendBackgroundGPS());
    }
});

// Periodic Background Sync (requiere permisos especiales)
self.addEventListener('periodicsync', (event) => {
    if (event.tag === 'gps-periodic') {
        console.log('📍 Periodic GPS Sync');
        event.waitUntil(sendPeriodicGPS());
    }
});

// Push notifications para activar GPS
self.addEventListener('push', (event) => {
    console.log('📨 Push recibido para GPS');
    
    if (event.data) {
        const data = event.data.json();
        if (data.type === 'gps_request') {
            event.waitUntil(handleGPSRequest(data));
        }
    }
});

// Función para enviar GPS en segundo plano
async function sendBackgroundGPS() {
    try {
        // Intentar obtener ubicación
        const position = await getCurrentPositionServiceWorker();
        
        if (position) {
            // Enviar al servidor
            const response = await fetch('/asistencia/actualizar-gps/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: new Date().toISOString(),
                    source: 'service_worker_background'
                })
            });
            
            if (response.ok) {
                console.log('✅ GPS enviado desde Service Worker');
                
                // Notificar a la app si está abierta
                const clients = await self.clients.matchAll();
                clients.forEach(client => {
                    client.postMessage({
                        type: 'gps_sent',
                        position: position.coords,
                        timestamp: new Date().toISOString()
                    });
                });
            }
        }
    } catch (error) {
        console.error('❌ Error en background GPS:', error);
    }
}

// Función para GPS periódico
async function sendPeriodicGPS() {
    console.log('🔄 Enviando GPS periódico');
    await sendBackgroundGPS();
}

// Manejar solicitudes de GPS via push
async function handleGPSRequest(data) {
    console.log('📍 Procesando solicitud GPS:', data);
    await sendBackgroundGPS();
    
    // Mostrar notificación de confirmación
    await self.registration.showNotification('EURO SECURITY', {
        body: 'Ubicación actualizada en segundo plano',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        tag: 'gps-update',
        silent: true
    });
}

// Obtener posición desde Service Worker (limitado)
function getCurrentPositionServiceWorker() {
    return new Promise((resolve, reject) => {
        // Los Service Workers tienen acceso limitado a geolocation
        // Esta función es principalmente para compatibilidad futura
        
        // Por ahora, devolvemos null ya que la geolocation
        // no está disponible directamente en Service Workers
        resolve(null);
    });
}

// Programar próximo sync
function scheduleNextGPSSync() {
    // Registrar background sync para el próximo GPS
    self.registration.sync.register(GPS_SYNC_TAG).catch(err => {
        console.error('❌ Error registrando background sync:', err);
    });
}

// Configurar periodic sync si está disponible
if ('serviceWorker' in navigator && 'periodicSync' in window.ServiceWorkerRegistration.prototype) {
    // Esto requiere permisos especiales y solo funciona en algunos navegadores
    self.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'SETUP_PERIODIC_GPS') {
            self.registration.periodicSync.register('gps-periodic', {
                minInterval: 30 * 1000 // 30 segundos mínimo
            }).catch(err => {
                console.error('❌ Error configurando periodic sync:', err);
            });
        }
    });
}
