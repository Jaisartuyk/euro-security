/**
 * Sistema de Captura Automática de Fotos de Seguridad
 * Euro Security - PWA
 */

class SecurityCamera {
    constructor() {
        this.isCapturing = false;
        this.captureInterval = null;
        this.intervalMinutes = 5; // Captura cada 5 minutos
        this.stream = null;
        this.lastCaptureTime = null;
        this.autoAnalyze = true; // Análisis IA automático
    }

    /**
     * Iniciar captura automática
     */
    async startAutoCapture(intervalMinutes = 5) {
        if (this.isCapturing) {
            console.log('⚠️ Captura automática ya está activa');
            return;
        }

        this.intervalMinutes = intervalMinutes;
        this.isCapturing = true;

        console.log(`📸 Iniciando captura automática cada ${intervalMinutes} minutos`);

        // Captura inmediata
        await this.captureAndSend();

        // Programar capturas periódicas
        this.captureInterval = setInterval(async () => {
            await this.captureAndSend();
        }, intervalMinutes * 60 * 1000);

        this.updateUI('active');
    }

    /**
     * Detener captura automática
     */
    stopAutoCapture() {
        if (!this.isCapturing) {
            console.log('⚠️ Captura automática no está activa');
            return;
        }

        console.log('⏹️ Deteniendo captura automática');

        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }

        this.isCapturing = false;
        this.updateUI('inactive');
    }

    /**
     * Capturar foto y enviar al servidor
     */
    async captureAndSend() {
        try {
            console.log('📸 Capturando foto...');

            // Obtener ubicación GPS
            const location = await this.getLocation();

            // Capturar foto
            const photoBlob = await this.capturePhoto();

            // Enviar al servidor
            const result = await this.sendToServer(photoBlob, location);

            this.lastCaptureTime = new Date();
            this.updateUI('success', result);

            console.log('✅ Foto enviada exitosamente', result);

            // Mostrar notificación si hay alertas
            if (result.has_alerts) {
                this.showAlert(result);
            }

        } catch (error) {
            console.error('❌ Error en captura:', error);
            this.updateUI('error', error);
        }
    }

    /**
     * Capturar foto desde cámara
     */
    async capturePhoto() {
        return new Promise(async (resolve, reject) => {
            try {
                // Obtener stream de cámara
                if (!this.stream) {
                    this.stream = await navigator.mediaDevices.getUserMedia({
                        video: {
                            facingMode: 'user', // Cámara frontal
                            width: { ideal: 1280 },
                            height: { ideal: 720 }
                        }
                    });
                }

                // Crear elemento video temporal
                const video = document.createElement('video');
                video.srcObject = this.stream;
                video.play();

                // Esperar a que el video esté listo
                await new Promise(resolve => {
                    video.onloadedmetadata = resolve;
                });

                // Crear canvas para captura
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;

                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0);

                // Convertir a blob
                canvas.toBlob(blob => {
                    resolve(blob);
                }, 'image/jpeg', 0.85);

            } catch (error) {
                reject(error);
            }
        });
    }

    /**
     * Obtener ubicación GPS
     */
    async getLocation() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocalización no soportada'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                position => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                error => {
                    console.warn('⚠️ Error obteniendo ubicación:', error);
                    resolve(null); // Continuar sin ubicación
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
    }

    /**
     * Enviar foto al servidor
     */
    async sendToServer(photoBlob, location) {
        const formData = new FormData();
        formData.append('photo', photoBlob, `security_${Date.now()}.jpg`);
        formData.append('capture_type', 'AUTO');
        formData.append('analyze_ai', this.autoAnalyze ? 'true' : 'false');

        if (location) {
            formData.append('latitude', location.latitude);
            formData.append('longitude', location.longitude);
        }

        // Obtener CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                         document.querySelector('meta[name="csrf-token"]')?.content;

        const response = await fetch('/asistencia/operaciones/fotos/capturar/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Mostrar alerta al usuario
     */
    showAlert(result) {
        // Notificación del navegador
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('🚨 Alerta de Seguridad', {
                body: `Nivel: ${result.alert_level}`,
                icon: '/static/icons/euro-security-icon.jpg',
                badge: '/static/icons/euro-security-icon.jpg',
                vibrate: [200, 100, 200]
            });
        }

        // Notificación en pantalla
        if (typeof showNotification === 'function') {
            showNotification('warning', `Alerta detectada: ${result.alert_level}`);
        }
    }

    /**
     * Actualizar UI
     */
    updateUI(status, data = null) {
        const statusElement = document.getElementById('camera-status');
        const lastCaptureElement = document.getElementById('last-capture-time');

        if (statusElement) {
            switch (status) {
                case 'active':
                    statusElement.innerHTML = '🟢 Captura Activa';
                    statusElement.className = 'badge bg-success';
                    break;
                case 'inactive':
                    statusElement.innerHTML = '⚪ Inactiva';
                    statusElement.className = 'badge bg-secondary';
                    break;
                case 'success':
                    if (lastCaptureElement) {
                        lastCaptureElement.textContent = new Date().toLocaleTimeString();
                    }
                    break;
                case 'error':
                    statusElement.innerHTML = '🔴 Error';
                    statusElement.className = 'badge bg-danger';
                    break;
            }
        }

        // Actualizar contador de fotos
        const photoCountElement = document.getElementById('photo-count');
        if (photoCountElement && status === 'success') {
            const currentCount = parseInt(photoCountElement.textContent) || 0;
            photoCountElement.textContent = currentCount + 1;
        }
    }

    /**
     * Solicitar permisos necesarios
     */
    async requestPermissions() {
        try {
            // Permiso de cámara
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());

            // Permiso de ubicación
            await this.getLocation();

            // Permiso de notificaciones
            if ('Notification' in window && Notification.permission === 'default') {
                await Notification.requestPermission();
            }

            console.log('✅ Permisos concedidos');
            return true;

        } catch (error) {
            console.error('❌ Error solicitando permisos:', error);
            return false;
        }
    }

    /**
     * Captura manual
     */
    async captureManual() {
        const originalAutoAnalyze = this.autoAnalyze;
        this.autoAnalyze = true; // Siempre analizar en captura manual

        await this.captureAndSend();

        this.autoAnalyze = originalAutoAnalyze;
    }
}

// Instancia global
const securityCamera = new SecurityCamera();

// Exportar para uso global
window.securityCamera = securityCamera;

// Auto-iniciar si está configurado
document.addEventListener('DOMContentLoaded', () => {
    // Verificar si el usuario tiene captura automática habilitada
    const autoCapture = localStorage.getItem('security_auto_capture');
    
    if (autoCapture === 'true') {
        // Solicitar permisos y iniciar
        securityCamera.requestPermissions().then(granted => {
            if (granted) {
                const interval = parseInt(localStorage.getItem('security_capture_interval')) || 5;
                securityCamera.startAutoCapture(interval);
            }
        });
    }
});

console.log('📸 Security Camera System loaded');
