/**
 * Script para forzar actualización de cache PWA
 * Especialmente útil cuando se actualizan iconos
 */

// Función para limpiar cache de PWA
async function clearPWACache() {
    try {
        // Limpiar todos los caches
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames.map(cacheName => caches.delete(cacheName))
            );
            console.log('✅ Cache PWA limpiado');
        }

        // Desregistrar service workers
        if ('serviceWorker' in navigator) {
            const registrations = await navigator.serviceWorker.getRegistrations();
            await Promise.all(
                registrations.map(registration => registration.unregister())
            );
            console.log('✅ Service Workers desregistrados');
        }

        return true;
    } catch (error) {
        console.error('❌ Error limpiando cache:', error);
        return false;
    }
}

// Función para forzar actualización del manifest
function forceManifestUpdate() {
    // Remover manifest link existente
    const existingManifest = document.querySelector('link[rel="manifest"]');
    if (existingManifest) {
        existingManifest.remove();
    }

    // Crear nuevo manifest link con timestamp
    const newManifest = document.createElement('link');
    newManifest.rel = 'manifest';
    newManifest.href = `/static/manifest.json?v=${Date.now()}`;
    document.head.appendChild(newManifest);
    
    console.log('✅ Manifest actualizado con timestamp');
}

// Función principal para actualizar PWA
async function updatePWA() {
    console.log('🔄 Iniciando actualización de PWA...');
    
    // 1. Limpiar cache
    await clearPWACache();
    
    // 2. Actualizar manifest
    forceManifestUpdate();
    
    // 3. Recargar página después de un delay
    setTimeout(() => {
        console.log('🔄 Recargando página...');
        window.location.reload(true);
    }, 1000);
}

// Auto-ejecutar si hay parámetro de actualización
if (window.location.search.includes('update_pwa=true')) {
    updatePWA();
}

// Hacer disponible globalmente
window.updatePWA = updatePWA;
window.clearPWACache = clearPWACache;
