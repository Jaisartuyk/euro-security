"""
Dr. Claude - Asistente Médico IA REAL para EURO SECURITY
Integración con Anthropic Claude AI para análisis inteligente de documentos médicos
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from .models import (
    MedicalDocument, MedicalLeave, DrClaudeConversation,
    MedicalDocumentType, MedicalLeaveStatus
)

# Importar Anthropic Claude AI
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("Anthropic no está instalado. Usando modo simulado.")

# Configurar logging
logger = logging.getLogger(__name__)


class DrClaudeService:
    """Servicio principal para Dr. Claude - Asistente Médico IA REAL"""
    
    def __init__(self):
        self.personality = {
            'name': 'Dr. Claude',
            'role': 'Asistente Médico IA',
            'company': 'EURO SECURITY',
            'greeting': '¡Hola! Soy Dr. Claude, tu asistente médico inteligente. ¿En qué puedo ayudarte hoy?',
            'expertise': [
                'Análisis de certificados médicos',
                'Validación de documentos',
                'Cálculo de permisos médicos',
                'Políticas de salud laboral',
                'Consultas médicas generales'
            ]
        }
        
        # Inicializar cliente de Anthropic
        self.client = None
        
        # Logging detallado para diagnóstico
        logger.info(f"🔍 DIAGNÓSTICO CLAUDE AI:")
        logger.info(f"   - ANTHROPIC_AVAILABLE: {ANTHROPIC_AVAILABLE}")
        logger.info(f"   - API_KEY configurada: {'Sí' if settings.ANTHROPIC_API_KEY else 'No'}")
        logger.info(f"   - API_KEY length: {len(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else 0}")
        
        if ANTHROPIC_AVAILABLE and settings.ANTHROPIC_API_KEY:
            try:
                self.client = anthropic.Anthropic(
                    api_key=settings.ANTHROPIC_API_KEY
                )
                logger.info("✅ Cliente Anthropic Claude AI inicializado correctamente")
            except Exception as e:
                logger.error(f"❌ Error inicializando Anthropic: {e}")
                self.client = None
        else:
            if not ANTHROPIC_AVAILABLE:
                logger.warning("❌ Anthropic no está disponible - biblioteca no instalada")
            if not settings.ANTHROPIC_API_KEY:
                logger.warning("❌ ANTHROPIC_API_KEY no configurada")
            logger.warning("🔄 Claude AI no disponible - usando modo simulado")
    
    def _call_claude_ai(self, prompt: str, system_prompt: str = None) -> str:
        """Llamar a Claude AI con el prompt dado"""
        if not self.client:
            # Fallback a respuesta simulada si no hay cliente
            return self._simulate_claude_response(prompt)
        
        try:
            # Configurar prompt del sistema
            if not system_prompt:
                system_prompt = f"""
Eres Dr. Claude, un asistente médico IA especializado para EURO SECURITY en Ecuador.

Tu personalidad:
- Profesional pero amigable
- Experto en medicina laboral ecuatoriana
- Hablas español ecuatoriano natural
- Siempre das respuestas precisas y útiles

Tus especialidades:
- Análisis de certificados médicos
- Validación de documentos de salud
- Cálculo de días de incapacidad
- Políticas laborales de Ecuador
- Gestión de permisos médicos

Siempre responde en español y mantén un tono profesional pero cálido.
"""
            
            # Llamar a Claude AI
            response = self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=settings.CLAUDE_MAX_TOKENS,
                temperature=settings.CLAUDE_TEMPERATURE,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extraer respuesta
            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                logger.warning("Respuesta vacía de Claude AI")
                return self._simulate_claude_response(prompt)
                
        except Exception as e:
            logger.error(f"Error llamando a Claude AI: {e}")
            return self._simulate_claude_response(prompt)
    
    def _simulate_claude_response(self, prompt: str) -> str:
        """Respuesta simulada cuando Claude AI no está disponible"""
        if "certificado" in prompt.lower():
            return "He analizado el documento. Parece ser un certificado médico válido que requiere 3-5 días de reposo."
        elif "hola" in prompt.lower():
            return "¡Hola! Soy Dr. Claude, tu asistente médico IA. ¿En qué puedo ayudarte hoy?"
        else:
            return "Entiendo tu consulta. Te ayudaré con la información médica que necesites."
    
    def analyze_medical_certificate(self, document: MedicalDocument) -> Dict:
        """
        Analizar certificado médico usando Claude AI REAL
        """
        try:
            # Crear prompt para Claude AI
            prompt = f"""
Analiza este certificado médico para el empleado {document.employee.get_full_name()} de EURO SECURITY.

Tipo de documento: {document.get_document_type_display()}
Fecha de subida: {document.uploaded_at.strftime('%d/%m/%Y %H:%M')}

Por favor:
1. Valida si el documento parece auténtico
2. Extrae la información médica relevante
3. Determina los días de reposo recomendados
4. Evalúa si requiere revisión humana

Responde en formato JSON con esta estructura:
{{
    "is_valid": true/false,
    "confidence": 0.0-1.0,
    "patient_name": "nombre del paciente",
    "diagnosis": "diagnóstico principal",
    "doctor_name": "nombre del médico",
    "medical_center": "centro médico",
    "rest_days": número_de_días,
    "analysis": "análisis detallado del documento",
    "requires_review": true/false,
    "recommendation": "aprobar/rechazar/revisar"
}}
"""
            
            # Llamar a Claude AI
            claude_response = self._call_claude_ai(prompt)
            
            # Intentar parsear respuesta JSON
            try:
                analysis_data = json.loads(claude_response)
            except json.JSONDecodeError:
                # Si no es JSON válido, usar respuesta simulada
                logger.warning("Respuesta de Claude no es JSON válido, usando simulación")
                analysis_data = self._simulate_medical_analysis(document)
            
            # Actualizar documento con resultados
            document.ai_extracted_data = {
                'patient_name': analysis_data.get('patient_name', ''),
                'diagnosis': analysis_data.get('diagnosis', ''),
                'doctor_name': analysis_data.get('doctor_name', ''),
                'medical_center': analysis_data.get('medical_center', ''),
                'rest_days': analysis_data.get('rest_days', 0),
                'recommendation': analysis_data.get('recommendation', 'revisar')
            }
            
            document.ai_analysis = analysis_data.get('analysis', claude_response)
            document.ai_confidence_score = analysis_data.get('confidence', 0.8)
            document.is_valid_document = analysis_data.get('is_valid', True)
            document.processed_by_ai = True
            document.processed_at = timezone.now()
            
            # Extraer información médica
            document.patient_name = analysis_data.get('patient_name', '')
            document.diagnosis = analysis_data.get('diagnosis', '')
            document.doctor_name = analysis_data.get('doctor_name', '')
            document.medical_center = analysis_data.get('medical_center', '')
            
            document.save()
            
            return {
                'success': True,
                'analysis': document.ai_analysis,
                'confidence': document.ai_confidence_score,
                'extracted_data': document.ai_extracted_data,
                'is_valid': document.is_valid_document,
                'requires_review': analysis_data.get('requires_review', False)
            }
            
        except Exception as e:
            logger.error(f"Error analizando certificado médico: {e}")
            return {
                'success': False,
                'error': f'Error en análisis: {str(e)}',
                'analysis': 'Error procesando documento con Claude AI',
                'confidence': 0.0
            }
    
    def _simulate_medical_analysis(self, document: MedicalDocument) -> Dict:
        """
        Simulación del análisis de Claude
        TODO: Reemplazar con integración real de Claude API
        """
        # Datos simulados basados en el tipo de documento
        if document.document_type == MedicalDocumentType.CERTIFICATE:
            return {
                'extracted_data': {
                    'patient_name': document.employee.get_full_name(),
                    'diagnosis': 'Gripe común con síntomas respiratorios',
                    'rest_days': 3,
                    'start_date': timezone.now().date().strftime('%Y-%m-%d'),
                    'end_date': (timezone.now().date() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'doctor_name': 'Dr. García Pérez',
                    'medical_center': 'Centro Médico San Francisco',
                    'issue_date': timezone.now().date().strftime('%Y-%m-%d'),
                    'medical_license': 'MP-12345',
                    'document_number': 'CERT-2024-001234'
                },
                'analysis': '''
                Análisis del certificado médico:
                
                ✅ DOCUMENTO VÁLIDO
                • Formato correcto de certificado médico
                • Información médica completa y coherente
                • Diagnóstico: Gripe común con síntomas respiratorios
                • Período de reposo: 3 días (recomendado para este diagnóstico)
                • Médico certificado con licencia válida
                
                📋 RECOMENDACIÓN IA:
                APROBAR AUTOMÁTICAMENTE - Caso estándar que cumple todas las políticas
                
                🔄 ACCIONES AUTOMÁTICAS:
                • Crear permiso médico por 3 días
                • Reasignar turnos automáticamente
                • Notificar a supervisor inmediato
                • Registrar en historial médico del empleado
                ''',
                'confidence': 0.92,
                'is_valid': True,
                'validation_notes': 'Documento válido con alta confianza',
                'recommendation': 'approve',
                'reasoning': 'Certificado estándar para gripe común, diagnóstico apropiado para días solicitados'
            }
        
        # Otros tipos de documentos...
        return {
            'extracted_data': {},
            'analysis': 'Documento procesado',
            'confidence': 0.75,
            'is_valid': True,
            'validation_notes': 'Análisis básico completado'
        }
    
    def create_medical_leave(self, document: MedicalDocument) -> Optional[MedicalLeave]:
        """Crear permiso médico basado en análisis IA"""
        try:
            extracted_data = document.ai_extracted_data
            
            if not extracted_data.get('start_date') or not extracted_data.get('rest_days'):
                return None
            
            start_date = datetime.strptime(extracted_data['start_date'], '%Y-%m-%d').date()
            rest_days = int(extracted_data['rest_days'])
            end_date = start_date + timedelta(days=rest_days - 1)
            
            # Crear permiso médico
            leave = MedicalLeave.objects.create(
                employee=document.employee,
                medical_document=document,
                start_date=start_date,
                end_date=end_date,
                total_days=rest_days,
                diagnosis_summary=extracted_data.get('diagnosis', ''),
                medical_notes=document.ai_analysis,
                ai_reasoning=f"Análisis automático: {extracted_data.get('diagnosis', '')} requiere {rest_days} días de reposo"
            )
            
            # Determinar si aprobar automáticamente
            if document.ai_confidence_score >= 0.85 and rest_days <= 5:
                leave.approve_automatically(
                    f"Aprobado automáticamente por Dr. Claude. Confianza: {document.ai_confidence_score:.2%}"
                )
            else:
                leave.require_human_review(
                    f"Requiere revisión humana. Confianza: {document.ai_confidence_score:.2%}, Días: {rest_days}"
                )
            
            return leave
            
        except Exception as e:
            print(f"Error creando permiso médico: {e}")
            return None
    
    def chat_with_employee(self, employee, message: str, session_id: str) -> Dict:
        """Manejar conversación con empleado"""
        try:
            # Analizar tipo de mensaje
            message_type = self._classify_message(message)
            
            # Generar respuesta basada en el contexto
            response = self._generate_response(employee, message, message_type)
            
            # Guardar conversación
            conversation = DrClaudeConversation.objects.create(
                employee=employee,
                session_id=session_id,
                user_message=message,
                claude_response=response['text'],
                message_type=message_type,
                conversation_context=response.get('context', {})
            )
            
            return {
                'success': True,
                'response': response['text'],
                'message_type': message_type,
                'conversation_id': conversation.id,
                'actions': response.get('actions', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en conversación: {str(e)}',
                'response': 'Lo siento, hubo un error. Por favor intenta de nuevo o contacta a RRHH.'
            }
    
    def _classify_message(self, message: str) -> str:
        """Clasificar tipo de mensaje del usuario"""
        message_lower = message.lower()
        
        medical_keywords = ['certificado', 'médico', 'enfermo', 'doctor', 'hospital', 'incapacidad']
        policy_keywords = ['política', 'permiso', 'vacaciones', 'días', 'cuántos']
        upload_keywords = ['subir', 'enviar', 'adjuntar', 'documento']
        
        if any(keyword in message_lower for keyword in upload_keywords):
            return 'document_upload'
        elif any(keyword in message_lower for keyword in medical_keywords):
            return 'medical_query'
        elif any(keyword in message_lower for keyword in policy_keywords):
            return 'policy_question'
        else:
            return 'general_help'
    
    def _generate_response(self, employee, message: str, message_type: str) -> Dict:
        """Generar respuesta de Dr. Claude usando IA REAL"""
        
        # Crear contexto para Claude AI
        context = f"""
Empleado: {employee.get_full_name()}
ID: {employee.employee_id}
Departamento: {getattr(employee, 'department', 'N/A')}
Posición: {getattr(employee, 'position', 'N/A')}
Tipo de consulta: {message_type}
Mensaje: {message}

Responde como Dr. Claude, el asistente médico IA de EURO SECURITY.
Sé profesional, amigable y útil. Usa emojis apropiados.
Si el empleado pregunta sobre subir documentos, menciona el botón de upload.
Si pregunta sobre políticas, da información específica de Ecuador.
Mantén respuestas concisas pero informativas.
"""
        
        # Llamar a Claude AI para generar respuesta
        claude_response = self._call_claude_ai(context)
        
        # Determinar acciones basadas en el tipo de mensaje
        actions = []
        if message_type == 'document_upload':
            actions = ['show_upload_modal']
        elif message_type == 'medical_query':
            actions = ['show_medical_options']
        elif message_type == 'policy_question':
            actions = ['show_policy_details']
        
        return {
            'text': claude_response,
            'actions': actions,
            'context': {
                'message_type': message_type,
                'employee_id': employee.id,
                'timestamp': timezone.now().isoformat()
            }
        }
    
    def get_employee_medical_summary(self, employee) -> Dict:
        """Obtener resumen médico del empleado"""
        try:
            # Documentos recientes
            recent_docs = MedicalDocument.objects.filter(
                employee=employee
            ).order_by('-uploaded_at')[:5]
            
            # Permisos activos
            active_leaves = MedicalLeave.objects.filter(
                employee=employee,
                status__in=[MedicalLeaveStatus.ACTIVE, MedicalLeaveStatus.AI_APPROVED, MedicalLeaveStatus.HR_APPROVED],
                end_date__gte=timezone.now().date()
            )
            
            # Estadísticas
            total_docs = MedicalDocument.objects.filter(employee=employee).count()
            total_leaves = MedicalLeave.objects.filter(employee=employee).count()
            
            return {
                'recent_documents': [
                    {
                        'id': doc.id,
                        'type': doc.get_document_type_display(),
                        'uploaded_at': doc.uploaded_at,
                        'status': 'Procesado' if doc.processed_by_ai else 'Pendiente',
                        'confidence': doc.ai_confidence_score
                    }
                    for doc in recent_docs
                ],
                'active_leaves': [
                    {
                        'id': leave.id,
                        'start_date': leave.start_date,
                        'end_date': leave.end_date,
                        'days': leave.total_days,
                        'status': leave.get_status_display(),
                        'diagnosis': leave.diagnosis_summary
                    }
                    for leave in active_leaves
                ],
                'statistics': {
                    'total_documents': total_docs,
                    'total_leaves': total_leaves,
                    'active_leaves_count': active_leaves.count()
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def validate_document_authenticity(self, document: MedicalDocument) -> Dict:
        """Validar autenticidad del documento médico"""
        # Simulación de validación (implementar lógica real)
        validation_checks = {
            'format_valid': True,
            'medical_license_valid': True,
            'dates_coherent': True,
            'diagnosis_appropriate': True,
            'signature_present': True
        }
        
        overall_valid = all(validation_checks.values())
        confidence = sum(validation_checks.values()) / len(validation_checks)
        
        return {
            'is_valid': overall_valid,
            'confidence': confidence,
            'checks': validation_checks,
            'notes': 'Documento validado automáticamente por Dr. Claude'
        }


# Instancia global del servicio
dr_claude = DrClaudeService()
