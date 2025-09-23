# 🚂 EURO SECURITY - Despliegue en Railway

## 🌟 ¿Por qué Railway?

- ✅ **Despliegue automático** desde Git
- ✅ **PostgreSQL incluido** gratis
- ✅ **HTTPS automático** con certificados SSL
- ✅ **Variables de entorno** fáciles de configurar
- ✅ **Escalamiento automático**
- ✅ **$5/mes** plan starter (muy económico)

---

## 🚀 Pasos para Desplegar

### 1️⃣ **Preparar Repositorio Git**
```bash
# Inicializar Git (si no está hecho)
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "🛡️ EURO SECURITY - Sistema completo con PWA y GPS tracking"

# Crear repositorio en GitHub/GitLab
# Subir código
git remote add origin https://github.com/tu-usuario/euro-security.git
git push -u origin main
```

### 2️⃣ **Configurar Railway**
1. **Ir a** [railway.app](https://railway.app)
2. **Login** con GitHub/GitLab
3. **New Project** → **Deploy from GitHub repo**
4. **Seleccionar** tu repositorio `euro-security`

### 3️⃣ **Agregar Base de Datos**
1. **En tu proyecto Railway** → **+ New**
2. **Database** → **Add PostgreSQL**
3. **Automáticamente** se crea `${{Postgres.DATABASE_URL}}`

### 4️⃣ **Configurar Variables de Entorno**
En **Settings** → **Variables**:

```bash
# Obligatorias
SECRET_KEY=tu-secret-key-django-aqui
DEBUG=False
ALLOWED_HOSTS=${{RAILWAY_STATIC_URL}},${{RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{Postgres.DATABASE_URL}}
GOOGLE_MAPS_API_KEY=AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ

# Opcionales
TIME_ZONE=America/Guayaquil
LANGUAGE_CODE=es-ec
```

### 5️⃣ **Desplegar**
1. **Railway detecta automáticamente** Django
2. **Build se ejecuta** con `nixpacks.toml`
3. **Deploy automático** en cada push a main

---

## 🔧 Configuración Post-Despliegue

### 📊 **Ejecutar Migraciones**
```bash
# En Railway Console o localmente
railway run python manage.py migrate

# Crear superusuario
railway run python manage.py createsuperuser

# Cargar datos de prueba (opcional)
railway run python create_simple_gps_data.py
```

### 🎯 **Verificar Funcionamiento**
1. **Abrir URL** de Railway (ej: `https://euro-security-production.up.railway.app`)
2. **Login** con superusuario
3. **Probar PWA** → Debe mostrar banner de instalación
4. **Verificar GPS** → Debe capturar ubicación
5. **Revisar mapas** → Deben cargar sin errores

---

## 📱 PWA en Railway

### ✅ **Automáticamente Habilitado:**
- 🔐 **HTTPS** → Certificado SSL automático
- 🌐 **Dominio personalizado** → `tu-app.up.railway.app`
- 📱 **Service Worker** → Se registra automáticamente
- 🛰️ **GPS Tracking** → Funciona en segundo plano
- 📲 **Instalación** → Banner aparece en móviles

### 🎯 **URLs Principales:**
```
https://tu-app.up.railway.app/
├── /admin/                    # Django Admin
├── /login/                    # Login sistema
├── /dashboard/                # Dashboard principal
├── /asistencia/               # Módulo asistencias
│   ├── /rastreo-tiempo-real/  # Mapa GPS tiempo real
│   ├── /mapa/                 # Mapa ubicaciones
│   └── /api/                  # APIs GPS
├── /empleados/                # Gestión empleados
├── /departamentos/            # Gestión departamentos
└── /reportes/                 # Reportes y estadísticas
```

---

## 💰 Costos Railway

### 🆓 **Plan Gratuito:**
- **$5 crédito mensual** gratis
- **PostgreSQL** incluido
- **HTTPS** incluido
- **Perfecto para desarrollo**

### 💳 **Plan Starter ($5/mes):**
- **$5 crédito** + $5 adicionales
- **Ideal para producción** pequeña-mediana
- **Escalamiento automático**
- **Soporte prioritario**

---

## 🔍 Monitoreo y Logs

### 📊 **Railway Dashboard:**
- **Metrics** → CPU, RAM, Network
- **Logs** → En tiempo real
- **Deployments** → Historial completo

### 🔧 **Comandos Útiles:**
```bash
# Ver logs en tiempo real
railway logs

# Conectar a base de datos
railway connect postgres

# Ejecutar comandos
railway run python manage.py shell

# Variables de entorno
railway variables
```

---

## 🛠️ Configuración Avanzada

### 🌐 **Dominio Personalizado:**
1. **Settings** → **Domains**
2. **Custom Domain** → `eurosecurity.com`
3. **Configurar DNS** → CNAME a Railway

### 📧 **Email (Opcional):**
```bash
# Agregar variables para email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### 🔐 **Seguridad Adicional:**
```bash
# Variables de seguridad
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

---

## ✅ Checklist de Despliegue

### 🔧 **Pre-despliegue:**
- [ ] Repositorio Git creado y pusheado
- [ ] `railway.json` y `nixpacks.toml` configurados
- [ ] Variables de entorno definidas
- [ ] Google Maps API Key válida

### 🚀 **Despliegue:**
- [ ] Proyecto Railway creado
- [ ] PostgreSQL agregado
- [ ] Variables configuradas
- [ ] Deploy exitoso

### ✅ **Post-despliegue:**
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] HTTPS funcionando
- [ ] PWA instalable
- [ ] GPS tracking activo
- [ ] Mapas cargando

---

## 🆘 Troubleshooting

### ❌ **Errores Comunes:**

**1. Build falla:**
```bash
# Verificar requirements.txt
# Revisar logs en Railway dashboard
```

**2. Base de datos no conecta:**
```bash
# Verificar DATABASE_URL en variables
# Ejecutar migraciones: railway run python manage.py migrate
```

**3. Static files no cargan:**
```bash
# Verificar collectstatic en nixpacks.toml
# Revisar STATIC_ROOT en settings
```

**4. PWA no instala:**
```bash
# Verificar HTTPS (debe estar activo)
# Revisar manifest.json en /static/
# Chrome DevTools → Application → Manifest
```

---

## 🎯 Ventajas de Railway vs Otras Plataformas

| Característica | Railway | Heroku | Vercel | Netlify |
|---|---|---|---|---|
| **PostgreSQL Gratis** | ✅ | ❌ ($9/mes) | ❌ | ❌ |
| **HTTPS Automático** | ✅ | ✅ | ✅ | ✅ |
| **Deploy desde Git** | ✅ | ✅ | ✅ | ✅ |
| **Precio Inicial** | $5/mes | $7/mes | $20/mes | $19/mes |
| **Configuración** | Muy fácil | Fácil | Medio | Medio |
| **Soporte Django** | ✅ Nativo | ✅ Nativo | ⚠️ Serverless | ❌ |

**🏆 Railway es la mejor opción para EURO SECURITY** por su simplicidad, precio y soporte completo para Django + PostgreSQL.

---

## 🚂 ¡Listo para Railway!

**Con esta configuración, EURO SECURITY estará funcionando en producción con:**
- 🛡️ **Sistema completo** de gestión empresarial
- 📱 **PWA instalable** con GPS tracking
- 🗺️ **Mapas en tiempo real** funcionando
- 🔐 **Reconocimiento facial** operativo
- 📊 **Dashboards** personalizados por nivel
- 🛰️ **APIs GPS** con autenticación completa

**¡Tu empresa de seguridad tendrá un sistema de clase mundial!** 🌟
