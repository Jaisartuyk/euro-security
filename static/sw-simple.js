/**
 * Service Worker Simple para desarrollo local
 * EURO SECURITY - Funcionalidades básicas en localhost
 */

const CACHE_NAME = 'euro-security-dev-v1.0.0';

// Archivos básicos para cachear
const CACHE_URLS = [
    '/',
    '/asistencia/dashboard/',
    '/asistencia/marcar/',
];

/**
 * INSTALACIÓN
 */
self.addEventListener('install', event => {
    console.log('🔧 Service Worker Simple: Instalando...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('📦 Cacheando recursos básicos');
                return cache.addAll(CACHE_URLS).catch(err => {
                    console.warn('⚠️ Algunos recursos no se pudieron cachear:', err);
                });
            })
            .then(() => {
                console.log('✅ Service Worker Simple instalado');
                return self.skipWaiting();
            })
    );
});

/**
 * ACTIVACIÓN
 */
self.addEventListener('activate', event => {
    console.log('🚀 Service Worker Simple: Activando...');
    
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
                console.log('✅ Service Worker Simple activado');
                return self.clients.claim();
            })
    );
});

/**
 * FETCH - Básico para desarrollo
 */
self.addEventListener('fetch', event => {
    // Solo interceptar GET requests
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Ignorar requests de extensiones del navegador
    if (event.request.url.startsWith('chrome-extension://') || 
        event.request.url.startsWith('moz-extension://')) {
        return;
    }
    
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Si la respuesta es exitosa, cachearla
                if (response.status === 200 && response.type === 'basic') {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseClone);
                        })
                        .catch(err => console.warn('⚠️ Error cacheando:', err));
                }
                return response;
            })
            .catch(() => {
                // Si falla, intentar desde cache
                return caches.match(event.request)
                    .then(response => {
                        if (response) {
                            return response;
                        }
                        
                        // Página offline básica
                        return new Response(`
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <title>Sin conexión - EURO SECURITY</title>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <style>
                                    body { 
                                        font-family: Arial, sans-serif; 
                                        text-align: center; 
                                        padding: 50px; 
                                        background: #f8f9fa;
                                    }
                                    .offline-container {
                                        max-width: 500px;
                                        margin: 0 auto;
                                        background: white;
                                        padding: 30px;
                                        border-radius: 10px;
                                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                                    }
                                    .offline-icon { font-size: 64px; margin-bottom: 20px; }
                                    .btn { 
                                        background: #007bff; 
                                        color: white; 
                                        padding: 10px 20px; 
                                        border: none; 
                                        border-radius: 5px; 
                                        cursor: pointer;
                                        text-decoration: none;
                                        display: inline-block;
                                        margin-top: 20px;
                                    }
                                </style>
                            </head>
                            <body>
                                <div class="offline-container">
                                    <div class="offline-icon">📴</div>
                                    <h1>Sin conexión</h1>
                                    <p>EURO SECURITY no puede conectarse al servidor.</p>
                                    <p>Verifica tu conexión a internet e intenta nuevamente.</p>
                                    <button class="btn" onclick="window.location.reload()">
                                        🔄 Reintentar
                                    </button>
                                </div>
                            </body>
                            </html>
                        `, {
                            headers: { 'Content-Type': 'text/html' }
                        });
                    });
            })
    );
});

/**
 * MENSAJES desde la aplicación
 */
self.addEventListener('message', event => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0].postMessage({ version: CACHE_NAME });
            break;
            
        case 'CLEAR_CACHE':
            caches.delete(CACHE_NAME).then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
    }
});

console.log('🚀 Service Worker Simple para desarrollo cargado');
