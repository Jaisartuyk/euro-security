# 🚂 VARIABLES DE ENTORNO PARA RAILWAY

## 📋 **CONFIGURAR EN RAILWAY DASHBOARD:**

### 🔧 **PASOS:**
1. **Ir a:** [railway.app](https://railway.app)
2. **Abrir** proyecto `high-pitched-fuel`
3. **Click** en servicio `euro-security`
4. **Ir a** pestaña **Variables**
5. **Agregar** estas variables:

### 🎯 **VARIABLES OBLIGATORIAS:**

```bash
SECRET_KEY=^@o*8&1_ou%em9$_#(8e37in^h=n05ki75kl_dgjozut^lr2do
DEBUG=False
ALLOWED_HOSTS=euro-security-production.up.railway.app,high-pitched-fuel-production.up.railway.app,localhost,127.0.0.1
DATABASE_URL=${{Postgres.DATABASE_URL}}
GOOGLE_MAPS_API_KEY=AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ
TIME_ZONE=America/Guayaquil
LANGUAGE_CODE=es-ec
```

### 🔐 **VARIABLES DE SEGURIDAD (OPCIONALES):**

```bash
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

## ✅ **DESPUÉS DE CONFIGURAR:**

1. **Railway** hará redeploy automáticamente
2. **Esperar** 2-3 minutos
3. **Abrir:** https://euro-security-production.up.railway.app
4. **Debería funcionar** sin errores

## 🎯 **VERIFICAR FUNCIONAMIENTO:**

- ✅ **Página carga** sin error ALLOWED_HOSTS
- ✅ **Login funciona** con admin/contraseña
- ✅ **PWA** muestra banner de instalación
- ✅ **GPS** captura ubicación
- ✅ **Mapas** cargan correctamente

## 🚨 **SI SIGUE FALLANDO:**

Agregar también estos dominios a ALLOWED_HOSTS:
```
*.up.railway.app
*.railway.app
```

**¡EURO SECURITY estará funcionando en producción!** 🛡️🚀
