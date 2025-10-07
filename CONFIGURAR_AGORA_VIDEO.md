# 📹 CONFIGURAR AGORA PARA VIDEO EN VIVO

## 🔍 PROBLEMA ACTUAL:

Error 500 al solicitar video porque faltan las credenciales de Agora.

Agora es el servicio de video streaming en tiempo real que permite:
- Video bidireccional entre operador y empleado
- Baja latencia (< 400ms)
- Alta calidad
- Escalable

---

## ✅ SOLUCIÓN: CONFIGURAR AGORA

### **Plan Gratuito de Agora:**
- 10,000 minutos gratis por mes
- Video HD
- Sin límite de usuarios concurrentes
- Sin tarjeta de crédito requerida

---

## 📝 PASOS PARA CONFIGURAR:

### **1. Crear Cuenta en Agora**

1. Ir a: https://console.agora.io/
2. Click en **"Sign Up"** (Registrarse)
3. Usar email o Google/GitHub
4. Verificar email
5. Completar perfil básico

### **2. Crear un Proyecto**

1. En el dashboard, click en **"Project Management"**
2. Click en **"Create"** (Crear proyecto)
3. Configurar:
   ```
   Project Name: Euro Security Video
   Use Case: Social
   Authentication: Secured mode: APP ID + Token
   ```
4. Click en **"Submit"**

### **3. Obtener Credenciales**

Después de crear el proyecto verás:

```
App ID: 1234567890abcdef1234567890abcdef
Primary Certificate: abcdef1234567890abcdef1234567890
```

**IMPORTANTE:** 
- El **App ID** es público (se usa en el frontend)
- El **Certificate** es secreto (solo en el backend)

### **4. Habilitar Token Authentication**

1. En tu proyecto, click en **"Config"**
2. En **"Primary Certificate"**, click en **"Enable"**
3. Copiar el Certificate que aparece
4. Click en **"Save"**

---

## 🔧 CONFIGURAR EN RAILWAY:

### **Variables a agregar:**

```
AGORA_APP_ID=tu_app_id_aqui
AGORA_APP_CERTIFICATE=tu_certificate_aqui
```

### **Pasos en Railway:**

1. Ir a tu proyecto en Railway
2. Click en tu servicio
3. Click en **"Variables"**
4. Agregar las 2 variables:

```
Variable 1:
Name: AGORA_APP_ID
Value: [Tu App ID de Agora]

Variable 2:
Name: AGORA_APP_CERTIFICATE
Value: [Tu Primary Certificate de Agora]
```

5. Railway desplegará automáticamente

---

## 🎯 CÓMO FUNCIONA EL VIDEO:

### **Flujo completo:**

```
1. OPERADOR (Dashboard):
   - Ve empleado en mapa
   - Click en "Solicitar Video"
   - Sistema genera token Agora

2. SERVIDOR (Django):
   - Crea VideoSession en BD
   - Genera 2 tokens Agora:
     * Token para operador
     * Token para empleado
   - Envía notificación push al empleado

3. EMPLEADO (PWA):
   - Recibe notificación push
   - Modal: "Operador solicita video"
   - Click en "Aceptar"
   - Se abre video con su token

4. VIDEO EN VIVO:
   - Conexión P2P via Agora
   - Video bidireccional
   - Audio bidireccional
   - Controles: mute, finalizar

5. FINALIZAR:
   - Cualquiera puede finalizar
   - Se guarda duración en BD
   - Se cierra conexión
```

---

## 🔍 VERIFICAR QUE FUNCIONA:

### **1. Ver logs de Railway:**
```
Buscar: "✅ Agora configured"
```

### **2. Probar solicitud de video:**

**Como Operador:**
1. Ir a `/asistencia/operaciones/`
2. Ver mapa con empleado
3. Click en marcador del empleado
4. Click en "📹 Solicitar Video"
5. Debería mostrar: "✅ Solicitud enviada"

**Como Empleado:**
1. Tener PWA abierta
2. Recibir notificación push
3. Modal: "Operador solicita video"
4. Click en "Aceptar"
5. Video debería iniciarse

---

## 📊 ARQUITECTURA DEL VIDEO:

```
┌─────────────────────────────────────────┐
│         OPERADOR (Dashboard)            │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Video Player (Agora SDK)       │  │
│  │   - Token: operador_token        │  │
│  │   - Channel: session_123         │  │
│  │   - Role: Publisher              │  │
│  └──────────────────────────────────┘  │
└─────────────────┬───────────────────────┘
                  │
                  │ Agora RTC
                  ▼
┌─────────────────────────────────────────┐
│         AGORA SERVERS (Cloud)           │
│                                         │
│  - Routing de video                     │
│  - Baja latencia (< 400ms)             │
│  - Escalable                            │
│  - Encriptado                           │
└─────────────────┬───────────────────────┘
                  │
                  │ Agora RTC
                  ▼
┌─────────────────────────────────────────┐
│         EMPLEADO (PWA)                  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   Video Player (Agora SDK)       │  │
│  │   - Token: empleado_token        │  │
│  │   - Channel: session_123         │  │
│  │   - Role: Publisher              │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 🆓 PLAN GRATUITO DE AGORA:

| Característica | Plan Gratuito |
|----------------|---------------|
| **Minutos/mes** | 10,000 |
| **Usuarios concurrentes** | Ilimitado |
| **Calidad video** | HD (1080p) |
| **Latencia** | < 400ms |
| **Regiones** | Global |
| **Soporte** | Comunidad |
| **Tarjeta requerida** | ❌ No |

**10,000 minutos = 166 horas de video por mes**

Si tienes 10 empleados y cada uno hace 1 sesión de 10 minutos al día:
- 10 empleados × 10 min × 22 días = 2,200 minutos/mes
- ✅ Dentro del plan gratuito

---

## ⚠️ IMPORTANTE:

### **Seguridad:**
- ✅ Tokens tienen expiración (1 hora por defecto)
- ✅ Cada sesión usa un canal único
- ✅ Certificate nunca se expone al frontend
- ✅ Solo backend genera tokens

### **Privacidad:**
- ⚠️ Video NO se graba por defecto
- ✅ Puedes habilitar grabación en Agora Console
- ✅ Grabaciones se guardan en Agora Cloud Storage
- ✅ Puedes descargarlas después

---

## 🔧 CONFIGURACIÓN ADICIONAL (OPCIONAL):

### **Habilitar Grabación de Video:**

1. En Agora Console → Tu proyecto
2. Click en **"Cloud Recording"**
3. Click en **"Enable"**
4. Configurar storage (AWS S3, Azure, etc.)
5. Guardar

### **Configurar Calidad de Video:**

En `static/js/video-live.js` puedes ajustar:

```javascript
const videoConfig = {
    mode: "rtc",
    codec: "vp8",
    // Calidad de video
    video: {
        width: 640,
        height: 480,
        frameRate: 30,
        bitrateMin: 400,
        bitrateMax: 1000
    }
};
```

---

## 📞 SOPORTE:

**Documentación oficial:**
- https://docs.agora.io/en/
- https://docs.agora.io/en/video-calling/get-started/get-started-sdk

**Ejemplos de código:**
- https://github.com/AgoraIO/API-Examples-Web

**Comunidad:**
- https://stackoverflow.com/questions/tagged/agora.io

---

## ✅ CHECKLIST:

- [ ] Crear cuenta en Agora
- [ ] Crear proyecto "Euro Security Video"
- [ ] Habilitar Token Authentication
- [ ] Copiar App ID
- [ ] Copiar Primary Certificate
- [ ] Agregar variables en Railway
- [ ] Esperar deploy (2-3 min)
- [ ] Verificar logs: "✅ Agora configured"
- [ ] Probar solicitud de video
- [ ] Verificar que funciona

---

**¿Listo para configurar Agora?** 🚀

Solo necesitas:
1. Crear cuenta (2 minutos)
2. Crear proyecto (1 minuto)
3. Copiar credenciales (30 segundos)
4. Agregar a Railway (1 minuto)

**Total: ~5 minutos** ⏱️
