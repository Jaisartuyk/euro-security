# 🚀 EURO SECURITY - Guía de Despliegue en Producción

## 📋 Opciones de Despliegue

### 🌐 1. HEROKU (Recomendado para inicio)

#### **Preparación:**
```bash
# 1. Instalar Heroku CLI
# Descargar desde: https://devcenter.heroku.com/articles/heroku-cli

# 2. Login en Heroku
heroku login

# 3. Crear aplicación
heroku create euro-security-app

# 4. Configurar variables de entorno
heroku config:set SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set GOOGLE_MAPS_API_KEY="AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ"

# 5. Configurar base de datos PostgreSQL
heroku addons:create heroku-postgresql:mini

# 6. Desplegar
git push heroku main
```

#### **Post-despliegue:**
```bash
# Ejecutar migraciones
heroku run python manage.py migrate

# Crear superusuario
heroku run python manage.py createsuperuser

# Verificar logs
heroku logs --tail
```

---

### 🔵 2. NETLIFY (Para frontend estático + API externa)

#### **Configuración:**
1. **Conectar repositorio** en Netlify
2. **Build settings:**
   - Build command: `python manage.py collectstatic --noinput`
   - Publish directory: `staticfiles`
3. **Environment variables:**
   - `SECRET_KEY`
   - `GOOGLE_MAPS_API_KEY`
   - `DATABASE_URL`

---

### ⚡ 3. VERCEL (Serverless)

#### **Configuración:**
```bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Login y deploy
vercel login
vercel --prod

# 3. Configurar variables en dashboard
# - SECRET_KEY
# - DATABASE_URL
# - GOOGLE_MAPS_API_KEY
```

---

### 🐳 4. DOCKER + VPS

#### **Dockerfile:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "security_hr_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### **docker-compose.yml:**
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/euro_security
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: euro_security
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 🔧 Configuración de Producción

### 📁 **Archivos necesarios:**
- ✅ `requirements.txt` → Dependencias Python
- ✅ `Procfile` → Comandos de Heroku
- ✅ `runtime.txt` → Versión de Python
- ✅ `.env.example` → Template de variables
- ✅ `.gitignore` → Archivos a ignorar

### 🔐 **Variables de entorno críticas:**
```bash
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:pass@host:port/dbname
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

### 🛡️ **Configuraciones de seguridad:**
```python
# En settings.py para producción
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 📱 PWA en Producción

### ✅ **Requisitos HTTPS:**
- 🔐 **Certificado SSL** obligatorio
- 🌐 **Dominio personalizado** recomendado
- 📱 **Service Worker** se activa automáticamente

### 🛰️ **GPS Tracking:**
- ✅ **Geolocation API** funciona en HTTPS
- ✅ **Background sync** disponible
- ✅ **Push notifications** activas
- ✅ **Instalación PWA** automática

---

## 🗺️ Google Maps en Producción

### 🔑 **API Key Configuration:**
1. **Google Cloud Console** → APIs & Services
2. **Habilitar APIs:**
   - Maps JavaScript API
   - Geolocation API
   - Places API (opcional)
3. **Restricciones:**
   - HTTP referrers: `yourdomain.com/*`
   - IP addresses (para servidor)

### 💰 **Costos estimados:**
- **Maps JavaScript API:** $7 por 1000 cargas
- **Geolocation API:** $5 por 1000 requests
- **Límite gratuito:** $200/mes en créditos

---

## 📊 Monitoreo y Logs

### 📈 **Heroku Logs:**
```bash
heroku logs --tail --app euro-security-app
```

### 🔍 **Sentry (Opcional):**
```bash
# Agregar a requirements.txt
sentry-sdk==1.38.0

# Configurar en settings.py
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

---

## ✅ Checklist de Despliegue

### 🔧 **Pre-despliegue:**
- [ ] Variables de entorno configuradas
- [ ] Base de datos PostgreSQL lista
- [ ] Google Maps API Key válida
- [ ] Archivos estáticos configurados
- [ ] SSL/HTTPS habilitado

### 🚀 **Post-despliegue:**
- [ ] Migraciones ejecutadas
- [ ] Superusuario creado
- [ ] Datos de prueba cargados
- [ ] PWA instalable
- [ ] GPS tracking funcionando
- [ ] Mapas cargando correctamente

### 🧪 **Testing:**
- [ ] Login/logout funcionando
- [ ] Reconocimiento facial activo
- [ ] Rastreo GPS en tiempo real
- [ ] APIs respondiendo correctamente
- [ ] PWA instalándose en móviles

---

## 🆘 Solución de Problemas

### ❌ **Errores comunes:**

**1. Static files no cargan:**
```bash
python manage.py collectstatic --noinput
```

**2. Base de datos no conecta:**
```bash
# Verificar DATABASE_URL
heroku config:get DATABASE_URL
```

**3. Google Maps no carga:**
```bash
# Verificar API Key y restricciones
# Console: https://console.cloud.google.com/
```

**4. PWA no instala:**
```bash
# Verificar HTTPS y manifest.json
# Chrome DevTools → Application → Manifest
```

---

## 📞 Soporte

**Para problemas técnicos:**
- 📧 Contactar al equipo de desarrollo
- 📚 Revisar documentación de Django
- 🌐 Consultar logs de la plataforma

**¡EURO SECURITY listo para producción!** 🛡️🚀
