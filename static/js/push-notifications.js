/**
 * Sistema de Notificaciones Push con Firebase
 * Euro Security - PWA
 */

class PushNotificationSystem {
    constructor() {
        this.messaging = null;
        this.token = null;
        this.isInitialized = false;
    }

    /**
     * Inicializar Firebase Messaging
     */
    async initialize(firebaseConfig) {
        try {
            // Verificar soporte
            if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
                console.warn('⚠️ Push notifications no soportadas');
                return false;
            }

            // Inicializar Firebase
            if (!firebase.apps.length) {
                firebase.initializeApp(firebaseConfig);
            }

            this.messaging = firebase.messaging();

            // Manejar mensajes en primer plano
            this.messaging.onMessage((payload) => {
                console.log('📬 Mensaje recibido:', payload);
                this.handleForegroundMessage(payload);
            });

            this.isInitialized = true;
            console.log('✅ Firebase Messaging inicializado');
            return true;

        } catch (error) {
            console.error('❌ Error inicializando Firebase:', error);
            return false;
        }
    }

    /**
     * Solicitar permiso y obtener token
     */
    async requestPermission() {
        try {
            // Solicitar permiso
            const permission = await Notification.requestPermission();

            if (permission !== 'granted') {
                console.warn('⚠️ Permiso de notificaciones denegado');
                return null;
            }

            // Obtener token
            this.token = await this.messaging.getToken({
                vapidKey: 'YOUR_VAPID_KEY' // TODO: Configurar VAPID key
            });

            console.log('✅ Token FCM obtenido:', this.token);

            // Guardar token en servidor
            await this.saveTokenToServer(this.token);

            return this.token;

        } catch (error) {
            console.error('❌ Error obteniendo token:', error);
            return null;
        }
    }

    /**
     * Guardar token en servidor
     */
    async saveTokenToServer(token) {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                             document.querySelector('meta[name="csrf-token"]')?.content;

            const response = await fetch('/api/save-fcm-token/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });

            if (response.ok) {
                console.log('✅ Token guardado en servidor');
                localStorage.setItem('fcm_token', token);
            }

        } catch (error) {
            console.error('❌ Error guardando token:', error);
        }
    }

    /**
     * Manejar mensaje en primer plano
     */
    handleForegroundMessage(payload) {
        const { notification, data } = payload;

        // Mostrar notificación personalizada
        this.showNotification(
            notification.title,
            notification.body,
            notification.icon,
            data
        );

        // Reproducir sonido
        this.playNotificationSound();

        // Vibrar
        if ('vibrate' in navigator) {
            navigator.vibrate([200, 100, 200]);
        }

        // Manejar según tipo
        if (data && data.type) {
            this.handleNotificationType(data);
        }
    }

    /**
     * Mostrar notificación
     */
    showNotification(title, body, icon, data = {}) {
        // Notificación del navegador
        if (Notification.permission === 'granted') {
            const notification = new Notification(title, {
                body,
                icon: icon || '/static/icons/euro-security-icon.jpg',
                badge: '/static/icons/euro-security-icon.jpg',
                tag: data.tag || 'euro-security',
                requireInteraction: data.priority === 'high',
                data: data
            });

            notification.onclick = () => {
                window.focus();
                notification.close();
                
                // Navegar según tipo
                if (data.url) {
                    window.location.href = data.url;
                }
            };
        }

        // Notificación en pantalla (toast)
        this.showToast(title, body, data.severity || 'info');
    }

    /**
     * Mostrar toast en pantalla
     */
    showToast(title, message, severity = 'info') {
        const toastHTML = `
            <div class="toast align-items-center text-white bg-${this.getSeverityColor(severity)} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${title}</strong><br>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        // Crear contenedor si no existe
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        // Agregar toast
        container.insertAdjacentHTML('beforeend', toastHTML);

        // Mostrar toast
        const toastElement = container.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
        toast.show();

        // Eliminar después de ocultar
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    /**
     * Obtener color según severidad
     */
    getSeverityColor(severity) {
        const colors = {
            'critical': 'danger',
            'high': 'danger',
            'medium': 'warning',
            'low': 'info',
            'info': 'info',
            'success': 'success'
        };
        return colors[severity] || 'info';
    }

    /**
     * Manejar según tipo de notificación
     */
    handleNotificationType(data) {
        switch (data.type) {
            case 'alert_critical':
                // Alerta crítica - mostrar modal
                this.showCriticalAlertModal(data);
                break;

            case 'video_request':
                // Solicitud de video - mostrar modal
                this.showVideoRequestModal(data);
                break;

            case 'photo_analyzed':
                // Foto analizada - actualizar UI
                if (typeof refreshData === 'function') {
                    refreshData();
                }
                break;

            case 'alert_resolved':
                // Alerta resuelta - actualizar UI
                if (typeof loadAlerts === 'function') {
                    loadAlerts();
                }
                break;
        }
    }

    /**
     * Mostrar modal de alerta crítica
     */
    showCriticalAlertModal(data) {
        const modalHTML = `
            <div class="modal fade" id="criticalAlertModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content border-danger">
                        <div class="modal-header bg-danger text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-exclamation-triangle"></i> ALERTA CRÍTICA
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <h6>${data.title || 'Alerta de Seguridad'}</h6>
                            <p>${data.message || 'Se ha detectado una situación crítica'}</p>
                            ${data.employee ? `<p><strong>Empleado:</strong> ${data.employee}</p>` : ''}
                            ${data.location ? `<p><strong>Ubicación:</strong> ${data.location}</p>` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                            ${data.alert_id ? `<button type="button" class="btn btn-primary" onclick="acknowledgeAlert(${data.alert_id})">Reconocer</button>` : ''}
                            ${data.url ? `<button type="button" class="btn btn-danger" onclick="window.location.href='${data.url}'">Ver Detalles</button>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar modal si no existe
        if (!document.getElementById('criticalAlertModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('criticalAlertModal'));
        modal.show();
    }

    /**
     * Mostrar modal de solicitud de video
     */
    showVideoRequestModal(data) {
        const modalHTML = `
            <div class="modal fade" id="videoRequestModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-video"></i> Solicitud de Video
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <p>${data.message || 'El centro de operaciones solicita una sesión de video'}</p>
                            ${data.requester ? `<p><strong>Solicitado por:</strong> ${data.requester}</p>` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Rechazar</button>
                            ${data.session_id ? `<button type="button" class="btn btn-success" onclick="acceptVideoRequest(${data.session_id})">Aceptar</button>` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar modal si no existe
        if (!document.getElementById('videoRequestModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('videoRequestModal'));
        modal.show();
    }

    /**
     * Reproducir sonido de notificación
     */
    playNotificationSound() {
        try {
            const audio = new Audio('/static/sounds/notification.mp3');
            audio.volume = 0.5;
            audio.play().catch(e => console.warn('No se pudo reproducir sonido:', e));
        } catch (error) {
            console.warn('Error reproduciendo sonido:', error);
        }
    }

    /**
     * Suscribirse a un topic
     */
    async subscribeToTopic(topic) {
        // Esto se maneja en el servidor
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                             document.querySelector('meta[name="csrf-token"]')?.content;

            await fetch('/api/subscribe-topic/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic, token: this.token })
            });

            console.log(`✅ Suscrito a topic: ${topic}`);

        } catch (error) {
            console.error('❌ Error suscribiéndose a topic:', error);
        }
    }
}

// Instancia global
const pushNotifications = new PushNotificationSystem();
window.pushNotifications = pushNotifications;

// Auto-inicializar si Firebase está configurado
document.addEventListener('DOMContentLoaded', () => {
    // TODO: Configurar con tus credenciales de Firebase
    const firebaseConfig = {
        apiKey: "YOUR_API_KEY",
        authDomain: "YOUR_AUTH_DOMAIN",
        projectId: "YOUR_PROJECT_ID",
        storageBucket: "YOUR_STORAGE_BUCKET",
        messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
        appId: "YOUR_APP_ID"
    };

    // Descomentar cuando Firebase esté configurado
    // pushNotifications.initialize(firebaseConfig);
});

console.log('🔔 Push Notification System loaded');
