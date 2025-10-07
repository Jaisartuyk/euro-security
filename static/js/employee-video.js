/**
 * Sistema de Video en Vivo para Empleados
 * Maneja solicitudes de video del operador
 */

class EmployeeVideoSystem {
    constructor() {
        this.checkInterval = null;
        this.currentSession = null;
        this.client = null;
        this.localTracks = {
            audioTrack: null,
            videoTrack: null
        };
    }

    /**
     * Iniciar verificación de solicitudes de video
     */
    startChecking() {
        if (this.checkInterval) return;

        this.checkInterval = setInterval(() => this.checkPendingRequests(), 5000);
        console.log('✅ Verificación de solicitudes de video iniciada');
    }

    /**
     * Verificar si hay solicitudes pendientes
     */
    async checkPendingRequests() {
        try {
            const response = await fetch('/asistencia/operaciones/video/pendiente/');
            const data = await response.json();

            if (data.has_pending && !this.currentSession) {
                this.showRequestModal(data.session);
            }
        } catch (error) {
            console.error('Error verificando solicitudes:', error);
        }
    }

    /**
     * Mostrar modal de solicitud
     */
    showRequestModal(session) {
        this.currentSession = session;

        const modalHTML = `
            <div class="modal fade" id="videoRequestModal" tabindex="-1" data-bs-backdrop="static">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-video"></i> Solicitud de Video
                            </h5>
                        </div>
                        <div class="modal-body text-center">
                            <div class="mb-3">
                                <i class="fas fa-video fa-3x text-primary"></i>
                            </div>
                            <h5>El operador solicita video en vivo</h5>
                            <p class="text-muted">¿Deseas aceptar?</p>
                            <div class="alert alert-info">
                                <small><i class="fas fa-info-circle"></i> Se activará tu cámara y micrófono</small>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" onclick="employeeVideo.reject()">
                                <i class="fas fa-times"></i> Rechazar
                            </button>
                            <button type="button" class="btn btn-success" onclick="employeeVideo.accept()">
                                <i class="fas fa-check"></i> Aceptar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('videoRequestModal'));
        modal.show();
    }

    /**
     * Aceptar solicitud
     */
    async accept() {
        try {
            const modal = bootstrap.Modal.getInstance(document.getElementById('videoRequestModal'));
            modal.hide();

            await this.joinChannel();
        } catch (error) {
            console.error('Error aceptando:', error);
            alert('Error: ' + error.message);
        }
    }

    /**
     * Rechazar solicitud
     */
    reject() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('videoRequestModal'));
        modal.hide();
        this.currentSession = null;

        setTimeout(() => {
            document.getElementById('videoRequestModal')?.remove();
        }, 500);
    }

    /**
     * Unirse al canal
     */
    async joinChannel() {
        try {
            console.log('📹 Conectando...', this.currentSession);

            this.client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });

            await this.client.join(
                this.currentSession.app_id,
                this.currentSession.channel_name,
                this.currentSession.employee_token,
                this.currentSession.employee_uid
            );

            console.log('✅ Conectado');

            this.localTracks.audioTrack = await AgoraRTC.createMicrophoneAudioTrack();
            this.localTracks.videoTrack = await AgoraRTC.createCameraVideoTrack();

            await this.client.publish([
                this.localTracks.audioTrack,
                this.localTracks.videoTrack
            ]);

            console.log('✅ Video publicado');

            this.showActiveModal();
        } catch (error) {
            console.error('❌ Error:', error);
            alert('Error: ' + error.message);
        }
    }

    /**
     * Mostrar modal de video activo
     */
    showActiveModal() {
        const modalHTML = `
            <div class="modal fade" id="activeVideoModal" tabindex="-1" data-bs-backdrop="static">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-success text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-video"></i> Video en Vivo
                            </h5>
                        </div>
                        <div class="modal-body">
                            <div class="text-center mb-3">
                                <span class="badge bg-danger">
                                    <i class="fas fa-circle"></i> EN VIVO
                                </span>
                            </div>
                            <div id="employee-video-container" style="width: 100%; height: 400px; background: #000; border-radius: 8px;"></div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-danger" onclick="employeeVideo.endCall()">
                                <i class="fas fa-phone-slash"></i> Finalizar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        const modal = new bootstrap.Modal(document.getElementById('activeVideoModal'));
        modal.show();

        // Mostrar video local
        this.localTracks.videoTrack.play('employee-video-container');
    }

    /**
     * Finalizar llamada
     */
    async endCall() {
        try {
            if (this.localTracks.audioTrack) {
                this.localTracks.audioTrack.close();
            }
            if (this.localTracks.videoTrack) {
                this.localTracks.videoTrack.close();
            }

            if (this.client) {
                await this.client.leave();
            }

            const modal = bootstrap.Modal.getInstance(document.getElementById('activeVideoModal'));
            modal.hide();

            setTimeout(() => {
                document.getElementById('activeVideoModal')?.remove();
                document.getElementById('videoRequestModal')?.remove();
            }, 500);

            this.currentSession = null;
            console.log('✅ Llamada finalizada');
        } catch (error) {
            console.error('Error finalizando:', error);
        }
    }
}

// Instancia global
const employeeVideo = new EmployeeVideoSystem();

// Auto-iniciar al cargar
document.addEventListener('DOMContentLoaded', () => {
    employeeVideo.startChecking();
    console.log('📹 Sistema de video del empleado cargado');
});
