# 🚀 APLICAR MIGRACIONES EN RAILWAY

## ✅ MÉTODO 1: Automático (Recomendado)

Railway debería aplicar las migraciones automáticamente después del deploy. Para verificar:

1. Ve a: https://railway.app/
2. Selecciona tu proyecto: **euro-security**
3. Click en **"Deployments"**
4. Busca el último deployment
5. Click en **"View Logs"**
6. Busca en los logs:
   ```
   Running migrations:
     Applying attendance.0011_add_security_ai_models... OK
   ```

Si ves esto, ✅ **las migraciones ya se aplicaron automáticamente**.

---

## ⚠️ MÉTODO 2: Manual (Si el automático falla)

Si NO ves las migraciones aplicadas en los logs, aplícalas manualmente:

### Opción A: Desde Railway CLI

1. Instala Railway CLI (si no lo tienes):
   ```bash
   npm i -g @railway/cli
   ```

2. Login en Railway:
   ```bash
   railway login
   ```

3. Conecta al proyecto:
   ```bash
   railway link
   ```
   Selecciona: **euro-security**

4. Ejecuta las migraciones:
   ```bash
   railway run python manage.py migrate attendance
   ```

### Opción B: Desde Railway Dashboard

1. Ve a: https://railway.app/
2. Selecciona tu proyecto: **euro-security**
3. Click en tu servicio (django app)
4. Click en **"Settings"**
5. Scroll hasta **"Deploy"**
6. En **"Custom Start Command"** temporalmente cambia a:
   ```
   python manage.py migrate && gunicorn security_hr_system.wsgi:application
   ```
7. Click **"Save"**
8. Railway hará redeploy automáticamente
9. Espera 2-3 minutos
10. Verifica en los logs que las migraciones se aplicaron
11. **IMPORTANTE**: Vuelve a cambiar el comando a solo:
    ```
    gunicorn security_hr_system.wsgi:application
    ```

---

## 🔍 VERIFICAR QUE LAS MIGRACIONES SE APLICARON

### Método 1: Desde Railway CLI
```bash
railway run python manage.py showmigrations attendance
```

Deberías ver:
```
attendance
 [X] 0001_initial
 [X] 0002_...
 ...
 [X] 0010_leaverequest
 [X] 0011_add_security_ai_models  ← ESTA DEBE TENER [X]
```

### Método 2: Desde Django Admin

1. Ve a: https://euro-security-production.up.railway.app/admin/
2. Login como superuser
3. Busca en la barra lateral:
   - **Attendance** → **Security Photos** ✅
   - **Attendance** → **Security Alerts** ✅
   - **Attendance** → **Video Sessions** ✅

Si ves estas opciones, ✅ **las migraciones están aplicadas**.

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error: "relation does not exist"

Si ves este error al intentar acceder a Security Photos:
```
ProgrammingError: relation "attendance_securityphoto" does not exist
```

**Solución:**
Las migraciones NO se aplicaron. Usa el **Método 2** arriba.

### Error: "No module named 'inference_sdk'"

Si ves este error en los logs:
```
ModuleNotFoundError: No module named 'inference_sdk'
```

**Solución:**
Railway no instaló las nuevas dependencias. Fuerza un rebuild:

1. Ve a Railway Dashboard
2. Click en **"Settings"**
3. Click en **"Redeploy"**
4. Selecciona **"Rebuild and Redeploy"**

---

## 📋 CHECKLIST DE VERIFICACIÓN

Después de aplicar las migraciones, verifica:

- [ ] Logs de Railway muestran: `Applying attendance.0011_add_security_ai_models... OK`
- [ ] `railway run python manage.py showmigrations` muestra `[X] 0011_add_security_ai_models`
- [ ] Django Admin muestra "Security Photos", "Security Alerts", "Video Sessions"
- [ ] No hay errores "relation does not exist" en los logs
- [ ] Dependencias instaladas: `inference-sdk`, `firebase-admin`, `agora-token-builder`

---

## ✅ CONFIRMACIÓN FINAL

Para confirmar que todo funciona:

1. Ve a: https://euro-security-production.up.railway.app/admin/attendance/securityphoto/
2. Deberías ver la página de administración de Security Photos
3. Si ves la página sin errores, ✅ **TODO ESTÁ FUNCIONANDO**

---

## 🆘 SI NADA FUNCIONA

Contacta conmigo y ejecutaremos las migraciones manualmente paso a paso.

**Comando de emergencia:**
```bash
railway run python manage.py migrate --run-syncdb
```

⚠️ **SOLO usa esto como último recurso**
