/**
 * Sistema de Video en Vivo con Agora
 * Euro Security - Centro de Operaciones
 */

class VideoLiveSystem {
    constructor() {
        this.client = null;
        this.localTracks = {
            videoTrack: null,
            audioTrack: null
        };
        this.remoteUsers = {};
        this.sessionId = null;
        this.channelName = null;
        this.token = null;
        this.appId = null;
        this.isJoined = false;
    }

    /**
     * Inicializar Agora SDK
     */
    async initialize(appId) {
        if (!window.AgoraRTC) {
            throw new Error('Agora SDK no cargado');
        }

        this.appId = appId;
        this.client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' });

        // Event listeners
        this.client.on('user-published', async (user, mediaType) => {
            await this.handleUserPublished(user, mediaType);
        });

        this.client.on('user-unpublished', (user, mediaType) => {
            this.handleUserUnpublished(user, mediaType);
        });

        this.client.on('user-left', (user) => {
            this.handleUserLeft(user);
        });

        console.log('✅ Agora SDK inicializado');
    }

    /**
     * Solicitar sesión de video a un empleado
     */
    async requestSession(employeeId) {
        try {
            console.log(`📹 Solicitando video a empleado ${employeeId}...`);

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                             document.querySelector('meta[name="csrf-token"]')?.content;

            const response = await fetch(`/asistencia/operaciones/video/solicitar/${employeeId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.sessionId = data.session_id;
                this.channelName = data.channel_name;
                this.token = data.requester_token;
                this.appId = data.app_id;
                this.uid = data.requester_uid; // UID del operador

                console.log('✅ Sesión de video creada:', data);
                console.log(`   - App ID: ${this.appId}`);
                console.log(`   - Canal: ${this.channelName}`);
                console.log(`   - UID: ${this.uid}`);

                // Mostrar modal de video
                this.showVideoModal();

                // Inicializar y unirse al canal
                await this.initialize(this.appId);
                await this.joinChannel();

                return data;
            } else {
                throw new Error(data.error || 'Error desconocido');
            }

        } catch (error) {
            console.error('❌ Error solicitando video:', error);
            throw error;
        }
    }

    /**
     * Unirse al canal de video
     */
    async joinChannel() {
        try {
            console.log(`🔗 Uniéndose al canal: ${this.channelName} con UID: ${this.uid}`);

            // Unirse al canal con el UID correcto
            await this.client.join(this.appId, this.channelName, this.token, this.uid);

            // Crear tracks locales
            this.localTracks.audioTrack = await AgoraRTC.createMicrophoneAudioTrack();
            this.localTracks.videoTrack = await AgoraRTC.createCameraVideoTrack();

            // Publicar tracks locales
            await this.client.publish([
                this.localTracks.audioTrack,
                this.localTracks.videoTrack
            ]);

            // Mostrar video local
            this.localTracks.videoTrack.play('local-video');

            this.isJoined = true;
            this.updateVideoStatus('connected');

            console.log('✅ Conectado al canal de video');

        } catch (error) {
            console.error('❌ Error uniéndose al canal:', error);
            this.updateVideoStatus('error');
            throw error;
        }
    }

    /**
     * Manejar usuario publicado
     */
    async handleUserPublished(user, mediaType) {
        console.log(`👤 Usuario publicó ${mediaType}:`, user.uid);

        // Suscribirse al usuario
        await this.client.subscribe(user, mediaType);

        this.remoteUsers[user.uid] = user;

        if (mediaType === 'video') {
            // Crear contenedor para video remoto
            const remoteContainer = document.getElementById('remote-video');
            if (remoteContainer) {
                user.videoTrack.play(remoteContainer);
            }
        }

        if (mediaType === 'audio') {
            user.audioTrack.play();
        }

        this.updateVideoStatus('streaming');
    }

    /**
     * Manejar usuario que dejó de publicar
     */
    handleUserUnpublished(user, mediaType) {
        console.log(`👤 Usuario dejó de publicar ${mediaType}:`, user.uid);

        if (mediaType === 'video') {
            const remoteContainer = document.getElementById('remote-video');
            if (remoteContainer) {
                remoteContainer.innerHTML = '<p class="text-center text-muted">Esperando video...</p>';
            }
        }
    }

    /**
     * Manejar usuario que salió
     */
    handleUserLeft(user) {
        console.log(`👤 Usuario salió:`, user.uid);
        delete this.remoteUsers[user.uid];

        const remoteContainer = document.getElementById('remote-video');
        if (remoteContainer) {
            remoteContainer.innerHTML = '<p class="text-center text-muted">Usuario desconectado</p>';
        }
    }

    /**
     * Salir del canal
     */
    async leaveChannel() {
        try {
            console.log('👋 Saliendo del canal...');

            // Detener tracks locales
            if (this.localTracks.audioTrack) {
                this.localTracks.audioTrack.stop();
                this.localTracks.audioTrack.close();
            }

            if (this.localTracks.videoTrack) {
                this.localTracks.videoTrack.stop();
                this.localTracks.videoTrack.close();
            }

            // Salir del canal
            if (this.client) {
                await this.client.leave();
            }

            this.isJoined = false;
            this.remoteUsers = {};

            // Finalizar sesión en servidor
            if (this.sessionId) {
                await this.endSession();
            }

            console.log('✅ Desconectado del canal');

        } catch (error) {
            console.error('❌ Error saliendo del canal:', error);
        }
    }

    /**
     * Finalizar sesión en servidor
     */
    async endSession() {
        try {
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                             document.querySelector('meta[name="csrf-token"]')?.content;

            const response = await fetch(`/asistencia/operaciones/video/${this.sessionId}/finalizar/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            console.log('✅ Sesión finalizada:', data);

        } catch (error) {
            console.error('❌ Error finalizando sesión:', error);
        }
    }

    /**
     * Silenciar/Activar audio
     */
    toggleAudio() {
        if (this.localTracks.audioTrack) {
            const enabled = this.localTracks.audioTrack.enabled;
            this.localTracks.audioTrack.setEnabled(!enabled);
            
            const btn = document.getElementById('toggle-audio-btn');
            if (btn) {
                btn.innerHTML = enabled ? '<i class="fas fa-microphone-slash"></i>' : '<i class="fas fa-microphone"></i>';
                btn.className = enabled ? 'btn btn-danger' : 'btn btn-primary';
            }
        }
    }

    /**
     * Activar/Desactivar video
     */
    toggleVideo() {
        if (this.localTracks.videoTrack) {
            const enabled = this.localTracks.videoTrack.enabled;
            this.localTracks.videoTrack.setEnabled(!enabled);
            
            const btn = document.getElementById('toggle-video-btn');
            if (btn) {
                btn.innerHTML = enabled ? '<i class="fas fa-video-slash"></i>' : '<i class="fas fa-video"></i>';
                btn.className = enabled ? 'btn btn-danger' : 'btn btn-primary';
            }
        }
    }

    /**
     * Mostrar modal de video
     */
    showVideoModal() {
        const modalHTML = `
            <div class="modal fade" id="videoLiveModal" tabindex="-1" data-bs-backdrop="static">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-video"></i> Video en Vivo
                            </h5>
                            <button type="button" class="btn-close btn-close-white" onclick="videoLive.closeModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-8">
                                    <div class="video-container" style="background: #000; border-radius: 10px; position: relative; height: 500px;">
                                        <div id="remote-video" style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
                                            <p class="text-white">Esperando conexión...</p>
                                        </div>
                                        <div id="local-video" style="position: absolute; bottom: 20px; right: 20px; width: 200px; height: 150px; border: 2px solid white; border-radius: 10px; overflow: hidden;"></div>
                                    </div>
                                    <div class="mt-3 text-center">
                                        <button id="toggle-audio-btn" class="btn btn-primary" onclick="videoLive.toggleAudio()">
                                            <i class="fas fa-microphone"></i>
                                        </button>
                                        <button id="toggle-video-btn" class="btn btn-primary" onclick="videoLive.toggleVideo()">
                                            <i class="fas fa-video"></i>
                                        </button>
                                        <button class="btn btn-danger" onclick="videoLive.closeModal()">
                                            <i class="fas fa-phone-slash"></i> Finalizar
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6 class="mb-0">Estado de la Sesión</h6>
                                        </div>
                                        <div class="card-body">
                                            <p><strong>Estado:</strong> <span id="video-status" class="badge bg-warning">Conectando...</span></p>
                                            <p><strong>Canal:</strong> <span id="channel-name">-</span></p>
                                            <p><strong>Duración:</strong> <span id="session-duration">00:00</span></p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar modal al DOM si no existe
        if (!document.getElementById('videoLiveModal')) {
            document.body.insertAdjacentHTML('beforeend', modalHTML);
        }

        // Mostrar modal
        const modal = new bootstrap.Modal(document.getElementById('videoLiveModal'));
        modal.show();

        // Actualizar información
        document.getElementById('channel-name').textContent = this.channelName || '-';

        // Iniciar contador de duración
        this.startDurationCounter();
    }

    /**
     * Cerrar modal
     */
    async closeModal() {
        await this.leaveChannel();
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('videoLiveModal'));
        if (modal) {
            modal.hide();
        }
    }

    /**
     * Actualizar estado del video
     */
    updateVideoStatus(status) {
        const statusElement = document.getElementById('video-status');
        if (!statusElement) return;

        switch (status) {
            case 'connected':
                statusElement.textContent = 'Conectado';
                statusElement.className = 'badge bg-success';
                break;
            case 'streaming':
                statusElement.textContent = 'En Vivo';
                statusElement.className = 'badge bg-success';
                break;
            case 'error':
                statusElement.textContent = 'Error';
                statusElement.className = 'badge bg-danger';
                break;
        }
    }

    /**
     * Contador de duración
     */
    startDurationCounter() {
        const startTime = Date.now();
        
        this.durationInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            const durationElement = document.getElementById('session-duration');
            if (durationElement) {
                durationElement.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            }
        }, 1000);
    }
}

// Instancia global
const videoLive = new VideoLiveSystem();
window.videoLive = videoLive;

console.log('📹 Video Live System loaded');
