# 📖 GUÍA DE USO - CENTRO DE OPERACIONES INTELIGENTE
## Euro Security - Manual del Usuario

**Versión:** 1.0  
**Fecha:** Octubre 2025

---

## 📋 ÍNDICE

1. [Acceso al Sistema](#acceso-al-sistema)
2. [Dashboard Principal](#dashboard-principal)
3. [Captura Automática de Fotos (Empleados)](#captura-automática-de-fotos)
4. [Monitoreo en Tiempo Real (Operadores)](#monitoreo-en-tiempo-real)
5. [Gestión de Alertas](#gestión-de-alertas)
6. [Video en Vivo](#video-en-vivo)
7. [Panel de Estadísticas](#panel-de-estadísticas)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🔐 ACCESO AL SISTEMA

### Para Empleados (PWA):

1. **Abrir la aplicación:**
   - URL: `https://euro-security-production.up.railway.app/`
   - Guardar en pantalla de inicio (PWA)

2. **Iniciar sesión:**
   - Usuario: Tu código de empleado
   - Contraseña: Tu contraseña asignada

3. **Permisos necesarios:**
   - ✅ Cámara
   - ✅ Ubicación GPS
   - ✅ Notificaciones

### Para Operadores (Dashboard):

1. **Acceder al Centro de Operaciones:**
   - URL: `https://euro-security-production.up.railway.app/asistencia/operaciones/`
   - Requiere: Usuario con permisos de **Staff** o **Superuser**

2. **Credenciales:**
   - Usuario: Tu usuario de operador
   - Contraseña: Tu contraseña asignada

---

## 📊 DASHBOARD PRINCIPAL

### ¿Qué verás?

El dashboard muestra en tiempo real:

#### **1. Estadísticas Rápidas** (Cards superiores)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ 📸 Fotos    │ ⚠️ Alertas  │ 🚨 Críticas │ 👥 Activos  │
│    Hoy      │   Activas   │             │             │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### **2. Mapa en Tiempo Real** (Izquierda)
- 🗺️ Ubicaciones GPS de empleados
- 🔵 Marcador azul: Empleado normal
- 🔴 Marcador rojo: Empleado con alerta
- 🔄 Actualización automática cada 30 segundos

#### **3. Panel de Alertas** (Derecha)
- 🚨 Alertas recientes ordenadas por severidad
- 🔴 CRÍTICA: Armas detectadas
- 🟠 ALTA: Comportamiento sospechoso
- 🟡 MEDIA: Sin EPP
- 🟢 BAJA: Informativas

#### **4. Grid de Fotos** (Inferior)
- 📸 Fotos recientes con alertas
- 🖼️ Miniaturas clickeables
- ⚠️ Badge de nivel de alerta

### Acciones Disponibles:

- 🔄 **Actualizar:** Refresca los datos manualmente
- 📸 **Capturar Foto:** Captura desde operaciones (futuro)
- 🔔 **Ver Alerta:** Click en alerta para detalles
- 📹 **Solicitar Video:** Click en empleado en mapa

---

## 📸 CAPTURA AUTOMÁTICA DE FOTOS

### Para Empleados:

#### **Paso 1: Activar Captura Automática**

1. Abre la aplicación PWA
2. Ve a **"Configuración"** o **"Seguridad"**
3. Activa **"Captura Automática"**
4. Selecciona intervalo (recomendado: **5 minutos**)

#### **Paso 2: Conceder Permisos**

El sistema solicitará:

```
┌─────────────────────────────────────┐
│  🎥 Permitir acceso a la cámara?   │
│  [ Permitir ] [ Bloquear ]         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  📍 Permitir acceso a ubicación?   │
│  [ Permitir ] [ Bloquear ]         │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  🔔 Permitir notificaciones?       │
│  [ Permitir ] [ Bloquear ]         │
└─────────────────────────────────────┘
```

**IMPORTANTE:** Debes permitir los 3 permisos.

#### **Paso 3: Sistema Activo**

Una vez activado:
- ✅ Captura foto cada 5 minutos
- ✅ Obtiene ubicación GPS automáticamente
- ✅ Envía al servidor
- ✅ Análisis IA automático
- ✅ Notificación si hay alerta

#### **Indicadores:**

```
Estado: 🟢 Captura Activa
Última foto: 16:30:45
Próxima foto: 16:35:45
Fotos hoy: 48
```

#### **Captura Manual:**

Si necesitas capturar una foto inmediatamente:
1. Click en botón **"📸 Capturar Ahora"**
2. La foto se enviará inmediatamente
3. Análisis IA automático

---

## 🎯 MONITOREO EN TIEMPO REAL

### Para Operadores:

#### **Ver Ubicaciones en Mapa:**

1. **Abrir Dashboard:**
   - URL: `/asistencia/operaciones/`

2. **Interactuar con Mapa:**
   - **Zoom:** Rueda del mouse o botones +/-
   - **Mover:** Arrastrar con mouse
   - **Click en marcador:** Ver información del empleado

3. **Información del Marcador:**
```
┌─────────────────────────────────┐
│  Juan Pérez                     │
│  Código: EMP001                 │
│  Área: Bodega Principal         │
│  ⚠️ ALERTA ACTIVA               │
│  [ 📹 Solicitar Video ]         │
└─────────────────────────────────┘
```

#### **Colores de Marcadores:**

- 🔵 **Azul:** Empleado sin alertas
- 🔴 **Rojo (pulsante):** Empleado con alerta activa
- ⚪ **Gris:** Empleado inactivo (>5 min sin señal)

#### **Auto-Refresh:**

El mapa se actualiza automáticamente cada **30 segundos**.

Para actualizar manualmente:
- Click en botón **"🔄 Actualizar"**

---

## 🚨 GESTIÓN DE ALERTAS

### Tipos de Alertas:

#### **1. CRÍTICA** 🔴🔴
- **Causa:** Arma detectada (pistola, rifle, cuchillo)
- **Acción:** Respuesta inmediata
- **Sonido:** Alarma fuerte
- **Modal:** Se abre automáticamente

#### **2. ALTA** 🔴
- **Causa:** Comportamiento sospechoso, vehículo no autorizado
- **Acción:** Investigar rápidamente
- **Sonido:** Alerta media

#### **3. MEDIA** 🟡
- **Causa:** Sin EPP (casco, chaleco)
- **Acción:** Notificar al empleado
- **Sonido:** Alerta suave

#### **4. BAJA** 🟢
- **Causa:** Informativas
- **Acción:** Revisar cuando sea posible

### Workflow de Alertas:

#### **Paso 1: Alerta Generada**

```
Estado: PENDING (Pendiente)
```

La alerta aparece en el panel derecho del dashboard.

#### **Paso 2: Reconocer Alerta**

1. Click en la alerta
2. Click en botón **"✓ Reconocer"**
3. Confirmar acción

```
Estado: ACKNOWLEDGED (Reconocida)
Reconocida por: [Tu nombre]
Timestamp: 16:35:20
```

#### **Paso 3: Investigar**

Opciones disponibles:
- 📸 **Ver Foto:** Click en miniatura
- 📍 **Ver Ubicación:** Ver en mapa
- 📹 **Solicitar Video:** Video en vivo
- 📊 **Ver Análisis IA:** Detalles de detección

#### **Paso 4: Resolver Alerta**

1. Click en botón **"✓ Resolver"**
2. Agregar notas:
```
┌─────────────────────────────────────┐
│  Notas de Resolución:               │
│  ┌─────────────────────────────┐   │
│  │ Falsa alarma. Objeto era    │   │
│  │ herramienta de trabajo.     │   │
│  └─────────────────────────────┘   │
│  [ Cancelar ] [ Resolver ]         │
└─────────────────────────────────────┘
```

```
Estado: RESOLVED (Resuelta)
Resuelta por: [Tu nombre]
Timestamp: 16:40:15
Notas: [Tus notas]
```

### Acciones Rápidas:

En el panel de alertas:
- **✓ Reconocer:** Marca como reconocida
- **✓ Resolver:** Marca como resuelta
- **❌ Falsa Alarma:** Marca como falsa alarma
- **📹 Video:** Solicita video al empleado

---

## 📹 VIDEO EN VIVO

### Solicitar Video a un Empleado:

#### **Paso 1: Solicitar**

**Opción A - Desde Mapa:**
1. Click en marcador del empleado
2. Click en **"📹 Solicitar Video"**

**Opción B - Desde Alerta:**
1. Click en alerta
2. Click en **"📹 Solicitar Video"**

#### **Paso 2: Esperar Respuesta**

El empleado recibe notificación push:
```
┌─────────────────────────────────────┐
│  📹 Solicitud de Video              │
│                                     │
│  El centro de operaciones solicita │
│  una sesión de video.               │
│                                     │
│  Solicitado por: Operador Juan     │
│                                     │
│  [ Rechazar ] [ Aceptar ]          │
└─────────────────────────────────────┘
```

#### **Paso 3: Video Activo**

Si el empleado acepta, se abre modal:

```
┌─────────────────────────────────────────────────┐
│  📹 Video en Vivo                               │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────┐           │
│  │                                 │           │
│  │     VIDEO DEL EMPLEADO          │           │
│  │         (Grande)                │           │
│  │                                 │           │
│  └─────────────────────────────────┘           │
│                                                 │
│  ┌─────────┐  ← Tu video (pequeño)            │
│  │  TÚ     │                                   │
│  └─────────┘                                   │
│                                                 │
│  [ 🎤 Mute ] [ 📹 Video ] [ ❌ Finalizar ]     │
│                                                 │
│  Estado: 🟢 En Vivo                            │
│  Duración: 02:35                               │
└─────────────────────────────────────────────────┘
```

#### **Controles Disponibles:**

- 🎤 **Mute Audio:** Silencia tu micrófono
- 📹 **Mute Video:** Apaga tu cámara
- ❌ **Finalizar:** Termina la sesión

#### **Paso 4: Finalizar**

Cualquiera puede finalizar:
- Operador: Click en **"❌ Finalizar"**
- Empleado: Click en **"❌ Finalizar"**

La sesión se guarda en la base de datos con:
- Duración
- Timestamp inicio/fin
- Participantes

---

## 📊 PANEL DE ESTADÍSTICAS

### Acceder a Analytics:

1. Desde Dashboard, click en **"📊 Analytics"**
2. O ir directamente a: `/asistencia/operaciones/analytics/`

### Qué Verás:

#### **1. Estadísticas Rápidas**

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 📸 1,234     │ 🚨 89        │ 🤖 94%       │ ⏱️ 45s       │
│ Fotos        │ Alertas      │ Precisión IA │ Respuesta    │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

#### **2. Gráficos Interactivos**

**Alertas por Día:**
- Gráfico de línea
- Últimos 7 días
- Tendencias visibles

**Alertas por Severidad:**
- Gráfico de dona
- Distribución por nivel
- Colores por severidad

**Detecciones IA:**
- Gráfico de barras
- Por tipo (armas, EPP, vehículos, personas)
- Total de detecciones

**Actividad por Hora:**
- Gráfico de barras
- 24 horas del día
- Picos de actividad

#### **3. Heatmap de Ubicaciones**

Mapa de calor mostrando:
- Zonas con más alertas
- Concentración de incidentes
- Áreas de riesgo

#### **4. Rankings**

**Top Empleados con Alertas:**
```
┌────────────────────┬─────────┬──────────┐
│ Empleado           │ Alertas │ Críticas │
├────────────────────┼─────────┼──────────┤
│ Juan Pérez         │ 15      │ 2        │
│ María González     │ 12      │ 0        │
│ Carlos Rodríguez   │ 8       │ 1        │
└────────────────────┴─────────┴──────────┘
```

**Top Áreas con Alertas:**
```
┌────────────────────┬─────────┬───────────┐
│ Área               │ Alertas │ Tendencia │
├────────────────────┼─────────┼───────────┤
│ Bodega Principal   │ 25      │ ↑ +15%    │
│ Estacionamiento    │ 18      │ ↓ -5%     │
│ Entrada Norte      │ 12      │ → 0%      │
└────────────────────┴─────────┴───────────┘
```

### Filtros de Tiempo:

```
┌─────────────────────────────┐
│ Rango: [ Última Semana ▼ ]  │
│                             │
│ • Hoy                       │
│ • Última Semana ✓           │
│ • Último Mes                │
└─────────────────────────────┘
```

---

## ❓ PREGUNTAS FRECUENTES

### Para Empleados:

**P: ¿Cada cuánto se capturan fotos?**  
R: Cada 5 minutos por defecto. Puedes configurarlo en ajustes.

**P: ¿Puedo desactivar la captura automática?**  
R: Sí, pero es requerido por política de seguridad. Consulta con RRHH.

**P: ¿Qué pasa si rechazo una solicitud de video?**  
R: El operador será notificado. Puede haber seguimiento de RRHH.

**P: ¿Se graban los videos?**  
R: Sí, todas las sesiones se registran con duración y participantes.

**P: ¿Consume muchos datos?**  
R: Fotos: ~200KB cada 5 min = ~2.4MB/hora. Video: ~1MB/min.

### Para Operadores:

**P: ¿Cómo sé si una alerta es real?**  
R: Revisa la foto, análisis IA, y solicita video si es necesario.

**P: ¿Puedo ver alertas antiguas?**  
R: Sí, en `/operaciones/fotos/` con filtros por fecha.

**P: ¿Qué hago con alertas críticas?**  
R: Protocolo de emergencia: Notificar supervisor, llamar seguridad.

**P: ¿Cuánto tiempo guarda el sistema las fotos?**  
R: 90 días por defecto. Consulta con IT para cambios.

**P: ¿Puedo exportar reportes?**  
R: Sí, desde el panel de analytics (próximamente).

---

## 🆘 SOPORTE

### Problemas Técnicos:

**Empleados:**
- Email: soporte@eurosecurity.com
- Teléfono: +593 XX XXX XXXX
- WhatsApp: +593 XX XXX XXXX

**Operadores:**
- Email: it@eurosecurity.com
- Teléfono: +593 XX XXX XXXX (Ext. 123)
- Slack: #soporte-operaciones

### Emergencias:

**Alerta Crítica:**
1. Notificar supervisor inmediatamente
2. Llamar a seguridad: XXX
3. Seguir protocolo de emergencia

---

## 📝 NOTAS IMPORTANTES

### Privacidad:

- ✅ Fotos solo visibles para operadores autorizados
- ✅ Datos encriptados en tránsito y reposo
- ✅ Cumplimiento GDPR y leyes locales
- ✅ Acceso auditado y registrado

### Mejores Prácticas:

**Empleados:**
- Mantén la app actualizada
- Carga tu dispositivo regularmente
- Reporta problemas técnicos inmediatamente
- No compartas tus credenciales

**Operadores:**
- Reconoce alertas rápidamente
- Documenta resoluciones claramente
- Usa video solo cuando sea necesario
- Respeta la privacidad de empleados

---

## 🎓 CAPACITACIÓN

### Videos Tutoriales:

1. **Introducción al Sistema** (5 min)
2. **Captura Automática para Empleados** (3 min)
3. **Dashboard para Operadores** (10 min)
4. **Gestión de Alertas** (8 min)
5. **Video en Vivo** (5 min)
6. **Analytics y Reportes** (7 min)

**Disponibles en:** [URL de capacitación]

### Certificación:

Completa el curso online y obtén tu certificación:
- **Empleados:** Certificado de Usuario
- **Operadores:** Certificado de Operador Nivel 1

---

**¿Necesitas más ayuda?**  
Contacta a soporte o consulta la documentación técnica.

---

**Desarrollado con ❤️ para Euro Security**  
**Versión:** 1.0 | **Fecha:** Octubre 2025
