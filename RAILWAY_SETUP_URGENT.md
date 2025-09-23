# 🚨 CONFIGURACIÓN URGENTE RAILWAY

## ❌ PROBLEMA ACTUAL:
```
OperationalError: no such table: auth_user
```

**CAUSA:** Railway está usando SQLite en lugar de PostgreSQL porque faltan variables de entorno.

## ✅ SOLUCIÓN INMEDIATA:

### 1️⃣ IR A RAILWAY DASHBOARD:
- URL: https://railway.app
- Login con GitHub (Jaisartuyk)
- Abrir proyecto: `high-pitched-fuel`

### 2️⃣ AGREGAR POSTGRESQL (si no existe):
- Click `+ New`
- `Database` → `Add PostgreSQL`

### 3️⃣ CONFIGURAR VARIABLES EN `euro-security`:
- Click en servicio `euro-security`
- Pestaña `Variables`
- Agregar estas variables:

```
SECRET_KEY=^@o*8&1_ou%em9$_#(8e37in^h=n05ki75kl_dgjozut^lr2do
DEBUG=True
ALLOWED_HOSTS=euro-security-production.up.railway.app,high-pitched-fuel-production.up.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
GOOGLE_MAPS_API_KEY=AIzaSyAtEPZgbPBwnJGrvIuwplRJDFbr0tmbnyQ
TIME_ZONE=America/Guayaquil
LANGUAGE_CODE=es-ec
```

### 4️⃣ DESPUÉS DEL REDEPLOY:
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python create_simple_gps_data.py
```

## 🎯 CREDENCIALES PARA CREAR:
```
Username: admin
Email: jairo1991st@hotmail.com
Password: admin123
```

## ✅ RESULTADO ESPERADO:
- ✅ PostgreSQL conectado
- ✅ Tablas creadas
- ✅ Usuario admin disponible
- ✅ Login funcionando
- ✅ EURO SECURITY operativo

**¡ESTE ES EL ÚLTIMO PASO PARA QUE FUNCIONE COMPLETAMENTE!** 🚀
