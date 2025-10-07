# 🧪 GUÍA DE PRUEBA RÁPIDA - CENTRO DE OPERACIONES
## Euro Security

---

## 🎯 OBJETIVO DE LA PRUEBA

Probar el flujo completo del Centro de Operaciones:
1. **Empleado** captura fotos (manual/automático)
2. **Admin** monitorea en tiempo real
3. **IA** analiza y genera alertas
4. **Admin** gestiona alertas

---

## 👥 USUARIOS PARA LA PRUEBA

### **Usuario 1: ADMIN** (Operador)
- **Rol:** Administrador / Staff
- **Permisos:** `is_staff = True` o `is_superuser = True`
- **Acceso a:**
  - ✅ Centro de Operaciones (`/asistencia/operaciones/`)
  - ✅ Analytics (`/asistencia/operaciones/analytics/`)
  - ✅ Admin Django (`/admin/`)

### **Usuario 2: ESPECIALISTA MARKETING** (Empleado)
- **Rol:** Especialista en Marketing Digital y Desarrollo
- **Permisos:** Usuario normal
- **Acceso a:**
  - ✅ Dashboard de empleado
  - ✅ Captura de fotos de seguridad
  - ❌ Centro de Operaciones (no tiene permisos)

---

## 📝 PASOS PARA LA PRUEBA

### **PASO 1: Dar Permisos de Staff al Admin** ✅

Si tu usuario admin ya tiene permisos de staff/superuser, **SALTA este paso**.

Si no, ejecuta:

```bash
python enable_operations_access.py
```

Ingresa tu username o email cuando te lo pida.

---

### **PASO 2: Iniciar Sesión como EMPLEADO (Marketing)**

1. **Ir a:** `https://euro-security-production.up.railway.app/`

2. **Iniciar sesión** con el usuario de Marketing

3. **Ir al Dashboard:**
   - Click en "Mi Dashboard Personal"
   - O ir a: `/employees/dashboard/`

4. **Buscar la card "Fotos de Seguridad":**
   ```
   ┌─────────────────────────────────────┐
   │  📸 Fotos de Seguridad             │
   │                                     │
   │  Captura fotos para el sistema     │
   │  de seguridad con IA.              │
   │                                     │
   │  [ 📸 Capturar Foto Ahora ]        │
   │  [ 🔄 Activar Automático ]         │
   │                                     │
   │  Estado: ⚪ Inactivo                │
   └─────────────────────────────────────┘
   ```

---

### **PASO 3: Capturar Foto MANUAL (Empleado)**

1. **Click en "📸 Capturar Foto Ahora"**

2. **Permitir acceso a la cámara:**
   ```
   ┌─────────────────────────────────────┐
   │  🎥 Permitir acceso a la cámara?   │
   │  [ Permitir ] [ Bloquear ]         │
   └─────────────────────────────────────┘
   ```
   ➡️ Click en **"Permitir"**

3. **Permitir acceso a la ubicación:**
   ```
   ┌─────────────────────────────────────┐
   │  📍 Permitir acceso a ubicación?   │
   │  [ Permitir ] [ Bloquear ]         │
   └─────────────────────────────────────┘
   ```
   ➡️ Click en **"Permitir"**

4. **Esperar mensaje de confirmación:**
   ```
   ✅ Foto capturada y enviada exitosamente!
   ```

5. **Verificar estado:**
   ```
   Estado: ✅ Foto enviada
   ```

**¡LISTO!** La foto fue enviada al servidor y está siendo analizada por la IA.

---

### **PASO 4: Activar Captura AUTOMÁTICA (Opcional)**

1. **Click en "🔄 Activar Automático"**

2. **Ingresar intervalo:**
   ```
   ¿Cada cuántos minutos deseas capturar fotos?
   [ 5 ]
   ```
   ➡️ Ingresa **5** (o el número que prefieras)

3. **Confirmar:**
   ```
   ✅ Captura automática activada cada 5 minutos
   ```

4. **Verificar estado:**
   ```
   Estado: 🟢 Activo (cada 5 min)
   ```

**¡LISTO!** Ahora se capturarán fotos automáticamente cada 5 minutos.

---

### **PASO 5: Monitorear como ADMIN (Operador)**

1. **Cerrar sesión del empleado**

2. **Iniciar sesión con usuario ADMIN**

3. **Ir al Dashboard de Empleado:**
   - `/employees/dashboard/`

4. **Buscar la card "Centro de Operaciones":**
   ```
   ┌─────────────────────────────────────┐
   │  🛡️ Centro de Operaciones          │
   │                                     │
   │  Monitoreo en tiempo real con IA   │
   │  y alertas de seguridad.           │
   │                                     │
   │  [ 👁️ Dashboard Operaciones ]      │
   │  [ 📊 Analytics ]                  │
   └─────────────────────────────────────┘
   ```

5. **Click en "👁️ Dashboard Operaciones"**

---

### **PASO 6: Ver Dashboard de Operaciones**

Deberías ver:

#### **Estadísticas (arriba):**
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ 📸 Fotos Hoy │ ⚠️ Alertas   │ 🚨 Críticas  │ 👥 Activos   │
│      1       │      0       │      0       │      1       │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

#### **Mapa (izquierda):**
```
┌─────────────────────────────────────┐
│  🗺️ MAPA EN TIEMPO REAL            │
│                                     │
│     🔵 ← Marcador del empleado     │
│                                     │
│  (Click en marcador para info)     │
└─────────────────────────────────────┘
```

#### **Panel de Alertas (derecha):**
```
┌─────────────────────────────────────┐
│  🚨 ALERTAS RECIENTES               │
│                                     │
│  (Vacío si no hay alertas)          │
│                                     │
│  O:                                 │
│  ⚠️ MEDIA - Sin EPP detectado       │
│  [ ✓ Reconocer ] [ 📹 Video ]      │
└─────────────────────────────────────┘
```

#### **Grid de Fotos (abajo):**
```
┌─────────────────────────────────────┐
│  📸 FOTOS RECIENTES CON ALERTAS     │
│                                     │
│  [Foto 1]  [Foto 2]  [Foto 3]      │
│  ⚠️ MEDIA   ✅ OK     🚨 ALTA       │
└─────────────────────────────────────┘
```

---

### **PASO 7: Interactuar con el Mapa**

1. **Click en el marcador azul** del empleado

2. **Ver información:**
   ```
   ┌─────────────────────────────────┐
   │  Especialista Marketing         │
   │  Código: EMP002                 │
   │  Área: Oficina                  │
   │  ⚪ Sin alertas                  │
   │  [ 📹 Solicitar Video ]         │
   └─────────────────────────────────┘
   ```

3. **Opciones:**
   - Ver información del empleado
   - Solicitar video en vivo (próximamente)

---

### **PASO 8: Ver Analytics**

1. **Click en "📊 Analytics"** (en el dashboard de empleado)
   
   O ir a: `/asistencia/operaciones/analytics/`

2. **Ver estadísticas:**
   - Total de fotos capturadas
   - Total de alertas generadas
   - Precisión de IA
   - Tiempo promedio de respuesta

3. **Ver gráficos:**
   - Alertas por día
   - Alertas por severidad
   - Detecciones IA
   - Actividad por hora

---

## ✅ CHECKLIST DE PRUEBA

### **Como Empleado:**
- [ ] Iniciar sesión
- [ ] Ver card "Fotos de Seguridad"
- [ ] Capturar foto manual
- [ ] Permitir cámara y GPS
- [ ] Ver confirmación de envío
- [ ] Activar captura automática (opcional)
- [ ] Configurar intervalo
- [ ] Verificar estado activo

### **Como Admin:**
- [ ] Iniciar sesión
- [ ] Ver card "Centro de Operaciones"
- [ ] Acceder a Dashboard Operaciones
- [ ] Ver estadísticas en tiempo real
- [ ] Ver mapa con empleado
- [ ] Click en marcador
- [ ] Ver información del empleado
- [ ] Acceder a Analytics
- [ ] Ver gráficos y estadísticas

---

## 🐛 TROUBLESHOOTING

### **Problema: No veo la card "Fotos de Seguridad"**
**Solución:** Refresca la página (Ctrl + F5)

### **Problema: No veo la card "Centro de Operaciones"**
**Solución:** 
1. Verifica que tu usuario tenga permisos de staff
2. Ejecuta `enable_operations_access.py`
3. Refresca la página

### **Problema: Error al capturar foto**
**Solución:**
1. Verifica que permitiste acceso a la cámara
2. Verifica que tu navegador soporte `getUserMedia`
3. Usa Chrome, Firefox o Edge (no IE)

### **Problema: No aparece el empleado en el mapa**
**Solución:**
1. Verifica que se capturó una foto con GPS
2. Espera 30 segundos (auto-refresh)
3. Click en "🔄 Actualizar"

### **Problema: "Page not found (404)"**
**Solución:**
1. Verifica que Railway haya desplegado los cambios
2. Espera 2-3 minutos después del push
3. Verifica la URL: `/asistencia/operaciones/`

---

## 📊 RESULTADOS ESPERADOS

### **Después de capturar 1 foto:**
- ✅ Foto visible en Admin Django (`/admin/attendance/securityphoto/`)
- ✅ Empleado aparece en mapa
- ✅ Estadística "Fotos Hoy" = 1
- ✅ Ubicación GPS guardada

### **Si la IA detecta algo:**
- ✅ Alerta generada automáticamente
- ✅ Visible en panel de alertas
- ✅ Marcador del empleado se pone rojo
- ✅ Estadística "Alertas Activas" aumenta

### **Con captura automática activa:**
- ✅ Fotos cada X minutos
- ✅ Estado "🟢 Activo"
- ✅ Persiste al recargar página

---

## 🎯 PRÓXIMOS PASOS

Una vez que la prueba funcione:

1. **Configurar Firebase** para notificaciones push
2. **Configurar Agora** para video en vivo
3. **Ajustar intervalos** de captura según necesidad
4. **Capacitar empleados** en el uso del sistema
5. **Monitorear alertas** y ajustar sensibilidad de IA

---

## 📞 SOPORTE

Si encuentras algún problema:
1. Revisa los logs de Railway
2. Revisa la consola del navegador (F12)
3. Contacta al equipo de desarrollo

---

**¡Buena suerte con la prueba!** 🚀
