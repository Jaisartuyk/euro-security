"""
Servicios de IA para Euro Security
Integración con Roboflow, Face++, Firebase y Agora
"""

import requests
import json
import base64
from django.conf import settings
from io import BytesIO
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class RoboflowService:
    """Servicio de detección de objetos con Roboflow"""
    
    def __init__(self):
        self.api_key = settings.ROBOFLOW_API_KEY
        self.api_url = settings.ROBOFLOW_API_URL
        self.models = settings.ROBOFLOW_MODELS
    
    def detect_weapons(self, image_path_or_bytes):
        """Detectar armas en una imagen"""
        return self._detect(image_path_or_bytes, 'weapon_detection')
    
    def detect_vehicles(self, image_path_or_bytes):
        """Detectar vehículos en una imagen"""
        return self._detect(image_path_or_bytes, 'vehicle_detection')
    
    def detect_ppe(self, image_path_or_bytes):
        """Detectar equipo de protección personal"""
        return self._detect(image_path_or_bytes, 'ppe_detection')
    
    def detect_persons(self, image_path_or_bytes):
        """Detectar personas en una imagen"""
        return self._detect(image_path_or_bytes, 'person_detection')
    
    def _detect(self, image_path_or_bytes, model_type):
        """Método genérico de detección"""
        try:
            from inference_sdk import InferenceHTTPClient
            
            client = InferenceHTTPClient(
                api_url=self.api_url,
                api_key=self.api_key
            )
            
            model_id = self.models.get(model_type)
            if not model_id:
                logger.error(f"Modelo {model_type} no configurado")
                return {'error': 'Modelo no configurado'}
            
            # Si es bytes, guardar temporalmente
            if isinstance(image_path_or_bytes, bytes):
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    tmp.write(image_path_or_bytes)
                    image_path = tmp.name
            else:
                image_path = image_path_or_bytes
            
            result = client.infer(image_path, model_id=model_id)
            
            logger.info(f"✅ Detección {model_type} exitosa: {len(result.get('predictions', []))} objetos")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en detección {model_type}: {str(e)}")
            return {'error': str(e), 'predictions': []}


class FacePlusPlusService:
    """Servicio de reconocimiento facial avanzado con Face++"""
    
    def __init__(self):
        self.api_key = settings.FACEPP_API_KEY
        self.api_secret = settings.FACEPP_API_SECRET
        self.api_url = settings.FACEPP_API_URL
    
    def detect_face(self, image_bytes):
        """Detectar rostro en imagen"""
        try:
            url = f"{self.api_url}/detect"
            
            files = {
                'image_file': ('image.jpg', image_bytes, 'image/jpeg')
            }
            
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'return_attributes': 'gender,age,emotion,facequality'
            }
            
            response = requests.post(url, files=files, data=data, timeout=10)
            result = response.json()
            
            if 'faces' in result and len(result['faces']) > 0:
                logger.info(f"✅ Face++ detectó {len(result['faces'])} rostro(s)")
                return result
            else:
                logger.warning("⚠️ Face++ no detectó rostros")
                return {'faces': []}
                
        except Exception as e:
            logger.error(f"❌ Error Face++ detect: {str(e)}")
            return {'error': str(e), 'faces': []}
    
    def compare_faces(self, image1_bytes, image2_bytes):
        """Comparar dos rostros"""
        try:
            url = f"{self.api_url}/compare"
            
            files = {
                'image_file1': ('image1.jpg', image1_bytes, 'image/jpeg'),
                'image_file2': ('image2.jpg', image2_bytes, 'image/jpeg')
            }
            
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret
            }
            
            response = requests.post(url, files=files, data=data, timeout=10)
            result = response.json()
            
            if 'confidence' in result:
                confidence = result['confidence']
                logger.info(f"✅ Face++ comparación: {confidence}% confianza")
                return result
            else:
                logger.warning("⚠️ Face++ no pudo comparar rostros")
                return {'confidence': 0}
                
        except Exception as e:
            logger.error(f"❌ Error Face++ compare: {str(e)}")
            return {'error': str(e), 'confidence': 0}
    
    def analyze_face_attributes(self, image_bytes):
        """Analizar atributos faciales (edad, género, emoción)"""
        result = self.detect_face(image_bytes)
        
        if result.get('faces'):
            face = result['faces'][0]
            attributes = face.get('attributes', {})
            
            return {
                'age': attributes.get('age', {}).get('value'),
                'gender': attributes.get('gender', {}).get('value'),
                'emotion': attributes.get('emotion', {}),
                'face_quality': attributes.get('facequality', {}).get('value'),
            }
        
        return None


class FirebaseService:
    """Servicio de notificaciones push con Firebase"""
    
    def __init__(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)
            
            self.messaging = messaging
            logger.info("✅ Firebase inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando Firebase: {str(e)}")
            self.messaging = None
    
    def send_notification(self, device_token, title, body, data=None):
        """Enviar notificación push a un dispositivo"""
        if not self.messaging:
            logger.error("❌ Firebase no inicializado")
            return False
        
        try:
            message = self.messaging.Message(
                notification=self.messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=device_token,
            )
            
            response = self.messaging.send(message)
            logger.info(f'✅ Notificación enviada: {response}')
            return True
            
        except Exception as e:
            logger.error(f'❌ Error enviando notificación: {str(e)}')
            return False
    
    def send_to_multiple(self, device_tokens, title, body, data=None):
        """Enviar notificación a múltiples dispositivos"""
        if not self.messaging:
            logger.error("❌ Firebase no inicializado")
            return None
        
        try:
            message = self.messaging.MulticastMessage(
                notification=self.messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=device_tokens,
            )
            
            response = self.messaging.send_multicast(message)
            logger.info(f'✅ Enviado a {response.success_count} dispositivos')
            logger.info(f'❌ Fallaron {response.failure_count} dispositivos')
            return response
            
        except Exception as e:
            logger.error(f'❌ Error: {str(e)}')
            return None


class AgoraService:
    """Servicio de video streaming con Agora"""
    
    def __init__(self):
        self.app_id = settings.AGORA_APP_ID
        self.app_certificate = settings.AGORA_APP_CERTIFICATE
        
        # Log de configuración (ocultar valores sensibles)
        if self.app_id:
            logger.info(f"🔧 Agora App ID configurado: {self.app_id[:8]}...")
        else:
            logger.warning("⚠️ Agora App ID NO configurado")
            
        if self.app_certificate:
            logger.info(f"🔧 Agora Certificate configurado: {self.app_certificate[:8]}...")
        else:
            logger.warning("⚠️ Agora Certificate NO configurado")
    
    def generate_rtc_token(self, channel_name, uid, role='publisher', expiration_time=3600):
        """Generar token RTC para video streaming"""
        try:
            from agora_token_builder import RtcTokenBuilder
            
            logger.info(f"📹 Generando token Agora:")
            logger.info(f"   - Canal: {channel_name}")
            logger.info(f"   - UID: {uid}")
            logger.info(f"   - Role: {role}")
            logger.info(f"   - App ID: {self.app_id[:8] if self.app_id else 'NONE'}...")
            logger.info(f"   - Certificate: {'OK' if self.app_certificate else 'NONE'}")
            
            # Determinar rol (1 = publisher, 2 = subscriber)
            # En la nueva versión, los roles son números
            if role == 'publisher':
                agora_role = 1  # Role.PUBLISHER
            else:
                agora_role = 2  # Role.SUBSCRIBER
            
            # Calcular tiempo de expiración
            import time
            current_timestamp = int(time.time())
            privilege_expired_ts = current_timestamp + expiration_time
            
            logger.info(f"   - Expira en: {expiration_time} segundos")
            
            # Generar token con la nueva API
            token = RtcTokenBuilder.buildTokenWithUid(
                self.app_id,
                self.app_certificate,
                channel_name,
                uid,
                agora_role,
                privilege_expired_ts
            )
            
            logger.info(f"✅ Token generado exitosamente: {token[:20]}...")
            return token
            
        except Exception as e:
            logger.error(f"❌ Error generando token Agora: {str(e)}")
            import traceback
            logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
    
    def create_video_session(self, employee_id, requester_id):
        """Crear sesión de video entre empleado y operador"""
        try:
            # Verificar que las credenciales estén configuradas
            if not self.app_id or not self.app_certificate:
                logger.error("❌ Credenciales de Agora no configuradas")
                raise ValueError("Credenciales de Agora no configuradas. Configura AGORA_APP_ID y AGORA_APP_CERTIFICATE en Railway.")
            
            import time
            channel_name = f"security_{employee_id}_{requester_id}_{int(time.time())}"
            
            logger.info(f"📹 Creando sesión de video: {channel_name}")
            
            # Token para el empleado (publisher)
            employee_token = self.generate_rtc_token(channel_name, employee_id, 'publisher')
            
            if not employee_token:
                raise ValueError("No se pudo generar token para empleado")
            
            # Token para el operador (publisher también, para video bidireccional)
            requester_token = self.generate_rtc_token(channel_name, requester_id, 'publisher')
            
            if not requester_token:
                raise ValueError("No se pudo generar token para operador")
            
            logger.info(f"✅ Sesión de video creada exitosamente: {channel_name}")
            
            return {
                'channel_name': channel_name,
                'app_id': self.app_id,
                'employee_token': employee_token,
                'requester_token': requester_token,
                'expires_in': 3600  # 1 hora
            }
        except Exception as e:
            logger.error(f"❌ Error creando sesión de video: {str(e)}")
            raise


# Instancias globales de servicios
roboflow_service = RoboflowService()
facepp_service = FacePlusPlusService()
firebase_service = FirebaseService()
agora_service = AgoraService()
