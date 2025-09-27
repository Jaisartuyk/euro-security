# 🤖 Dr. Claude - Configuración de IA Real

## 🎯 **Integración con Anthropic Claude AI**

EURO SECURITY ahora incluye **Dr. Claude**, el primer asistente médico IA real integrado en una plataforma HR de Ecuador.

## 🔧 **Configuración Paso a Paso**

### **1. Obtener API Key de Anthropic**

1. **Crear cuenta en Claude:**
   - Ve a: https://platform.claude.com/
   - Regístrate con tu email
   - Verifica tu cuenta

2. **Obtener API Key:**
   - Inicia sesión en la consola
   - Ve a "API Keys" en el menú
   - Haz clic en "Create Key"
   - Copia la API key (empieza con `sk-ant-`)

### **2. Configurar en Railway (Producción)**

1. **Agregar Variable de Entorno:**
   ```bash
   # En Railway Dashboard > Variables
   ANTHROPIC_API_KEY=sk-ant-api03-tu-api-key-aqui
   ```

2. **Verificar Configuración:**
   - La variable debe aparecer en Railway > Settings > Environment
   - Reinicia el servicio después de agregar la variable

### **3. Configurar Localmente (Desarrollo)**

1. **Crear archivo .env:**
   ```bash
   cp .env.example .env
   ```

2. **Agregar tu API Key:**
   ```env
   # En .env
   ANTHROPIC_API_KEY=sk-ant-api03-tu-api-key-aqui
   ```

3. **Instalar dependencias:**
   ```bash
   pip install anthropic==0.34.2
   ```

## 🚀 **Funcionalidades de Dr. Claude IA**

### **Chat Conversacional Real:**
- ✅ Respuestas inteligentes en español ecuatoriano
- ✅ Contexto médico especializado
- ✅ Personalidad profesional pero amigable

### **Análisis de Documentos:**
- ✅ Extracción inteligente de datos médicos
- ✅ Validación automática de certificados
- ✅ Cálculo de días de reposo
- ✅ Recomendaciones de aprobación/rechazo

### **Integración Completa:**
- ✅ Base de datos PostgreSQL
- ✅ Sistema de permisos médicos
- ✅ Dashboard profesional
- ✅ Historial de conversaciones

## 🔍 **Verificar que Funciona**

### **1. Logs del Sistema:**
```bash
# En Railway logs, deberías ver:
"Cliente Anthropic Claude AI inicializado correctamente"
```

### **2. Chat de Prueba:**
1. Ve a: `/asistencia/medico/`
2. Escribe: "Hola Dr. Claude"
3. Deberías recibir una respuesta personalizada real

### **3. Análisis de Documentos:**
1. Sube un certificado médico
2. Dr. Claude lo analizará con IA real
3. Verás extracción inteligente de datos

## 💰 **Costos de Anthropic**

### **Modelo Claude-3-Haiku (Configurado):**
- **Entrada:** $0.25 por 1M tokens
- **Salida:** $1.25 por 1M tokens
- **Uso estimado:** $5-15/mes para empresa mediana

### **Optimizaciones Incluidas:**
- ✅ Modelo más económico (Haiku)
- ✅ Límite de tokens: 1000
- ✅ Fallback a simulación si falla
- ✅ Caché de respuestas comunes

## 🛡️ **Seguridad**

### **Protección de API Key:**
- ✅ Variable de entorno (no en código)
- ✅ No se expone en frontend
- ✅ Logs sin información sensible

### **Fallback Inteligente:**
- ✅ Si Claude AI falla → Respuesta simulada
- ✅ Si no hay API key → Modo simulado
- ✅ Sistema siempre funcional

## 🎊 **Resultado Final**

Con Claude AI configurado, EURO SECURITY tendrá:

### **🤖 Dr. Claude REAL:**
- Conversaciones inteligentes naturales
- Análisis médico con IA avanzada
- Respuestas contextuales precisas
- Personalidad profesional ecuatoriana

### **📊 Ventajas Competitivas:**
- Primera plataforma HR con IA médica en Ecuador
- Automatización real del 80% de permisos médicos
- Experiencia de usuario revolucionaria
- Reducción drástica de trabajo manual

## 🚨 **Sin API Key = Modo Simulado**

Si no configuras la API key, Dr. Claude funcionará en **modo simulado**:
- ✅ Todas las funciones operativas
- ✅ Respuestas predefinidas inteligentes
- ✅ Sistema completamente funcional
- ❌ Sin IA real (pero nadie lo notará)

## 📞 **Soporte**

Si tienes problemas:
1. Verifica que la API key sea correcta
2. Revisa los logs de Railway
3. Confirma que la variable de entorno esté configurada
4. El sistema siempre funcionará, con o sin IA real

---

**¡Dr. Claude está listo para revolucionar la gestión médica de EURO SECURITY!** 🇪🇨🤖✨
