# 🚀 EURO SECURITY - Configuración GitHub + Railway

## 📋 **PASOS EXACTOS PARA DESPLIEGUE**

### 1️⃣ **CREAR REPOSITORIO EN GITHUB**

1. **Ir a:** [github.com/new](https://github.com/new)
2. **Repository name:** `euro-security`
3. **Description:** `🛡️ EURO SECURITY - Sistema de gestión empresarial con PWA y GPS tracking`
4. **Visibility:** `Public` (o Private si prefieres)
5. **NO marcar:** "Add a README file" (ya tenemos uno)
6. **NO marcar:** "Add .gitignore" (ya tenemos uno)
7. **NO marcar:** "Choose a license"
8. **Click:** `Create repository`

### 2️⃣ **SUBIR CÓDIGO A GITHUB**

Ejecutar estos comandos en tu terminal:

```bash
# Ya configurado:
# git remote add origin https://github.com/Jaisartuyk/euro-security.git
# git branch -M main

# Subir el código:
git push -u origin main
```

### 3️⃣ **VERIFICAR EN GITHUB**

Después del push, deberías ver en `https://github.com/Jaisartuyk/euro-security`:
- ✅ 150+ archivos subidos
- ✅ README.md con descripción
- ✅ Carpetas: attendance, employees, departments, etc.
- ✅ Archivos de Railway: railway.json, nixpacks.toml

---

## 🚂 **DESPLEGAR EN RAILWAY**

### 4️⃣ **CONFIGURAR RAILWAY**

1. **Ir a:** [railway.app](https://railway.app)
2. **Login** con GitHub (usar cuenta Jaisartuyk)
3. **New Project** → **Deploy from GitHub repo**
4. **Buscar y seleccionar:** `Jaisartuyk/euro-security`
5. **Deploy** → Railway detectará automáticamente Django

### 5️⃣ **AGREGAR BASE DE DATOS**

1. **En tu proyecto Railway** → **+ New**
2. **Database** → **Add PostgreSQL**
3. **Automáticamente** se crea la variable `${{Postgres.DATABASE_URL}}`

### 6️⃣ **CONFIGURAR VARIABLES DE ENTORNO**

En **Settings** → **Variables**, agregar:

```bash
SECRET_KEY=django-insecure-tu-clave-super-secreta-aqui-cambiar-en-produccion
DEBUG=False
ALLOWED_HOSTS=${{RAILWAY_STATIC_URL}},${{RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
GOOGLE_MAPS_API_KEY=AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ
TIME_ZONE=America/Guayaquil
LANGUAGE_CODE=es-ec
```

### 7️⃣ **EJECUTAR MIGRACIONES**

Una vez desplegado, en Railway **Console**:

```bash
# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
# Username: admin
# Email: admin@eurosecurity.com
# Password: [tu contraseña segura]

# Cargar datos de prueba GPS
python create_simple_gps_data.py
```

---

## ✅ **VERIFICAR FUNCIONAMIENTO**

### 8️⃣ **PROBAR LA APLICACIÓN**

Tu app estará en: `https://euro-security-production.up.railway.app`

**Verificar:**
- ✅ **Login** funciona
- ✅ **Dashboard** carga correctamente
- ✅ **PWA** muestra banner de instalación (en móvil)
- ✅ **GPS** captura ubicación
- ✅ **Mapas** cargan sin errores
- ✅ **Reconocimiento facial** activo

### 9️⃣ **PROBAR PWA EN MÓVIL**

1. **Abrir** la URL en Chrome móvil
2. **Debería aparecer** banner "Instalar EURO SECURITY"
3. **Instalar** como app nativa
4. **Probar GPS** → Debe capturar ubicación cada 30 segundos
5. **Verificar offline** → Debe funcionar sin internet

---

## 🎯 **URLs PRINCIPALES**

Una vez desplegado:

```
https://euro-security-production.up.railway.app/
├── /admin/                    # Django Admin
├── /login/                    # Login sistema
├── /dashboard/                # Dashboard principal
├── /empleados/                # Gestión empleados
├── /departamentos/            # Gestión departamentos
├── /puestos/                  # Gestión puestos
├── /reportes/                 # Reportes
└── /asistencia/               # Módulo asistencias
    ├── /                      # Marcación facial
    ├── /dashboard/            # Dashboard asistencias
    ├── /rastreo-tiempo-real/  # 🗺️ Mapa GPS tiempo real
    ├── /mapa/                 # 🗺️ Mapa ubicaciones
    ├── /alertas-ubicacion/    # 🚨 Alertas GPS
    └── /api/                  # APIs GPS
```

---

## 🆘 **SOLUCIÓN DE PROBLEMAS**

### ❌ **Si el push a GitHub falla:**
```bash
# Verificar remote
git remote -v

# Si no está configurado:
git remote add origin https://github.com/Jaisartuyk/euro-security.git

# Forzar push si es necesario
git push -u origin main --force
```

### ❌ **Si Railway no detecta Django:**
- Verificar que `requirements.txt` esté en la raíz
- Verificar que `railway.json` esté presente
- Revisar logs en Railway dashboard

### ❌ **Si las migraciones fallan:**
```bash
# En Railway console
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### ❌ **Si Google Maps no carga:**
- Verificar que `GOOGLE_MAPS_API_KEY` esté configurada
- Revisar restricciones de la API Key en Google Cloud Console

---

## 💰 **COSTOS ESTIMADOS**

### 🚂 **Railway:**
- **Starter Plan:** $5/mes
- **Incluye:** PostgreSQL + HTTPS + SSL + Deploy automático

### 🗺️ **Google Maps:**
- **Gratuito:** $200/mes en créditos
- **Estimado:** $10-30/mes según uso real

### 💡 **Total:** $15-35/mes para empresa pequeña-mediana

---

## 🎉 **¡LISTO PARA PRODUCCIÓN!**

**Con estos pasos, EURO SECURITY estará funcionando en producción con:**
- 🛡️ **Sistema completo** de gestión empresarial
- 📱 **PWA instalable** con GPS tracking
- 🗺️ **Mapas en tiempo real** funcionando
- 🔐 **Reconocimiento facial** operativo
- 📊 **Dashboards** personalizados
- 🛰️ **APIs GPS** autenticadas

**¡Tu empresa tendrá un sistema de clase mundial!** 🌟

---

**👤 Usuario GitHub:** `Jaisartuyk`
**📦 Repositorio:** `https://github.com/Jaisartuyk/euro-security`
**🚂 Railway:** Deploy automático desde GitHub
**🌐 Producción:** HTTPS automático con certificados SSL
