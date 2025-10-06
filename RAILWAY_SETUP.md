# 🚀 CONFIGURACIÓN DE VARIABLES EN RAILWAY

## 📋 INSTRUCCIONES PASO A PASO

### 1. Ir a Railway Dashboard
1. Ve a: https://railway.app/
2. Selecciona tu proyecto: **euro-security**
3. Click en tu servicio (django app)
4. Click en la pestaña **"Variables"**

---

### 2. Agregar Variables de Entorno

Copia y pega cada variable **UNA POR UNA** en Railway:

#### ✅ Face++ (Reconocimiento Facial)
```
FACEPP_API_KEY=PYESOaVo9aBrA93Za8VJ8N-MCn8K4I9a
FACEPP_API_SECRET=gPJ3vlzR3JPcquaf8jyAns1ydewrlNSs
```

#### ✅ Roboflow (Detección de Objetos con IA)
```
ROBOFLOW_API_KEY=EpoRz6PzSsiIyfsAHNlW
```

#### ✅ Firebase (Notificaciones Push)
```
FIREBASE_PROJECT_ID=euro-security
```

**FIREBASE_CREDENTIALS_JSON** (TODO EN UNA SOLA LÍNEA):
```
FIREBASE_CREDENTIALS_JSON=<COPIAR_DESDE_.env.railway>
```
*Nota: Copia el JSON completo desde el archivo `.env.railway` que está en tu computadora local*

**FIREBASE_VAPID_KEY** (Obtener de Firebase Console):
```
FIREBASE_VAPID_KEY=TU_VAPID_KEY_AQUI
```
*Nota: Ve a Firebase Console → Cloud Messaging → Web Push certificates → Generate key pair*

#### ✅ Agora (Video Streaming)
```
AGORA_APP_ID=721736ea50a54a028950c35785860c51
AGORA_APP_CERTIFICATE=007eJxTYBCwnbZmdlH1nrmbmo+9l/OeebmPk/uTVVPF49f82kdupV1SYDA3MjQ3NktNNDVINDVJNDCysDQ1SDY2NbcwtTAzSDY1lFR5ktEQyMiQUL2eiZEBAkF8HobU0qL84tTk0qLMkkoGBgB1eCKw
```

---

### 3. Verificar Variables

Después de agregar todas las variables, verifica que estén configuradas:

```
✅ FACEPP_API_KEY
✅ FACEPP_API_SECRET
✅ ROBOFLOW_API_KEY
✅ FIREBASE_PROJECT_ID
✅ FIREBASE_CREDENTIALS_JSON
✅ FIREBASE_VAPID_KEY
✅ AGORA_APP_ID
✅ AGORA_APP_CERTIFICATE
```

---

### 4. Redeploy

Railway hará redeploy automáticamente al detectar las nuevas variables.

Espera 2-3 minutos y verifica en los logs que no haya errores.

---

## 🎯 MODELOS ROBOFLOW CONFIGURADOS

Los siguientes modelos ya están configurados en `settings.py`:

1. **Detección de Armas**: `weapon-detection-pgqnr/7`
2. **Detección de Vehículos**: `vehicle-detection-byizq/2`
3. **Detección de EPP**: `ppe-detection-kfpqi/1`
4. **Detección de Personas**: `person-detection-j44uo/1`

---

## ✅ VERIFICACIÓN

Para verificar que todo funciona:

1. Ve a los logs de Railway
2. Busca mensajes como:
   ```
   ✅ Face++ API configurada
   ✅ Roboflow API configurada
   ✅ Firebase inicializado
   ✅ Agora configurado
   ```

3. No debe aparecer:
   ```
   ⚠️ Warning: FIREBASE_CREDENTIALS_JSON no es un JSON válido
   ```

---

## 🚨 IMPORTANTE

- **NO** subas el archivo `.env.railway` a GitHub
- **NO** compartas estas credenciales públicamente
- Las credenciales ya están en `.gitignore`

---

## 📞 SOPORTE

Si tienes problemas:
1. Verifica que copiaste las variables correctamente
2. Asegúrate de que FIREBASE_CREDENTIALS_JSON esté en UNA SOLA LÍNEA
3. Revisa los logs de Railway para errores específicos
