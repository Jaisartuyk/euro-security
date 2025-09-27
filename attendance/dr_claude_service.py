"""
Dr. Claude - Asistente Médico IA
EURO SECURITY - Servicio de IA para análisis médico
"""
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.utils import timezone
from .models import (
    MedicalDocument, MedicalLeave, DrClaudeConversation,
    MedicalDocumentType, MedicalLeaveStatus
)


class DrClaudeService:
    """Servicio principal para Dr. Claude - Asistente Médico IA"""
    
    def __init__(self):
        self.personality = {
            "name": "Dr. Claude",
            "role": "Asistente Médico Inteligente de EURO SECURITY",
            "greeting": "¡Hola! Soy Dr. Claude, tu asistente médico inteligente. ¿En qué puedo ayudarte hoy?",
            "expertise": [
                "Análisis de certificados médicos",
                "Validación de documentos de salud",
                "Cálculo de días de incapacidad",
                "Políticas laborales de Ecuador",
                "Gestión de permisos médicos"
            ]
        }
    
    def analyze_medical_certificate(self, document: MedicalDocument) -> Dict:
        """
        Analizar certificado médico usando IA simulada
        En producción, aquí iría la integración con Claude API
        """
        try:
            # Simulación de análisis IA (reemplazar con Claude API real)
            analysis_result = self._simulate_claude_analysis(document)
            
            # Guardar análisis en el documento
            document.ai_extracted_data = analysis_result['extracted_data']
            document.ai_analysis = analysis_result['analysis']
            document.ai_confidence_score = analysis_result['confidence']
            document.is_valid_document = analysis_result['is_valid']
            document.validation_notes = analysis_result['validation_notes']
            
            # Extraer campos específicos
            extracted = analysis_result['extracted_data']
            document.patient_name = extracted.get('patient_name', '')
            document.diagnosis = extracted.get('diagnosis', '')
            document.doctor_name = extracted.get('doctor_name', '')
            document.medical_center = extracted.get('medical_center', '')
            
            if extracted.get('issue_date'):
                try:
                    document.issue_date = datetime.strptime(
                        extracted['issue_date'], '%Y-%m-%d'
                    ).date()
                except:
                    pass
            
            document.mark_as_processed()
            
            return analysis_result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en análisis: {str(e)}',
                'confidence': 0.0
            }
    
    def _simulate_claude_analysis(self, document: MedicalDocument) -> Dict:
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
        """Generar respuesta de Dr. Claude"""
        
        responses = {
            'document_upload': {
                'text': f'''¡Perfecto, {employee.first_name}! 📄
                
Para subir tu certificado médico:

1. 📤 Haz clic en "Subir Certificado Médico"
2. 📷 Toma una foto clara del documento o selecciona el archivo
3. 🤖 Yo me encargaré automáticamente de:
   • Extraer todos los datos médicos
   • Validar la información
   • Calcular los días de permiso
   • Reasignar tus turnos
   • Notificar a tu supervisor

¿Tienes el certificado listo para subir?''',
                'actions': ['show_upload_modal']
            },
            
            'medical_query': {
                'text': f'''¡Hola {employee.first_name}! 👨‍⚕️

Como tu asistente médico, puedo ayudarte con:

🏥 **Certificados Médicos:**
• Procesamiento automático en segundos
• Validación de documentos
• Cálculo de días de reposo

📋 **Permisos Médicos:**
• Creación automática de solicitudes
• Seguimiento de estado
• Historial médico personal

💊 **Consultas de Salud:**
• Políticas de incapacidad
• Procedimientos médicos
• Derechos laborales

¿Qué necesitas específicamente?''',
                'actions': ['show_medical_options']
            },
            
            'policy_question': {
                'text': f'''📚 **Políticas Médicas - EURO SECURITY**

Hola {employee.first_name}, aquí tienes la información:

🏥 **Permisos por Enfermedad:**
• Hasta 5 días: Aprobación automática con certificado
• Más de 5 días: Revisión de RRHH
• Certificado médico obligatorio desde el 1er día

📅 **Días Disponibles:**
• Tienes derecho a permisos médicos según el Código de Trabajo
• Sin límite para enfermedades certificadas
• Reposo por maternidad: 12 semanas

⏰ **Tiempos de Procesamiento:**
• Análisis automático: Inmediato
• Aprobación IA: 2-5 minutos
• Revisión humana: 24-48 horas

¿Necesitas información específica sobre algún tema?''',
                'actions': ['show_policy_details']
            },
            
            'general_help': {
                'text': f'''¡Hola {employee.first_name}! 👋 Soy Dr. Claude, tu asistente médico inteligente.

🤖 **¿Cómo puedo ayudarte?**

🏥 **Gestión Médica:**
• Subir certificados médicos
• Consultar permisos activos
• Ver historial de salud

💬 **Consultas:**
• Políticas de incapacidad
• Procedimientos médicos
• Derechos laborales

📞 **Contacto Humano:**
• Si necesitas hablar con RRHH
• Casos complejos o urgentes

Escribe tu consulta o selecciona una opción. ¡Estoy aquí para ayudarte! 😊'''
            }
        }
        
        return responses.get(message_type, responses['general_help'])
    
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
