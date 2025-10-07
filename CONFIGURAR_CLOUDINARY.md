# 📸 CONFIGURAR CLOUDINARY PARA IMÁGENES PERSISTENTES

## 🔍 PROBLEMA ACTUAL:

Railway usa **almacenamiento efímero** - cada vez que se despliega, se pierden los archivos subidos.

Las fotos se guardan en la base de datos pero las imágenes físicas se pierden al reiniciar.

---

## ✅ SOLUCIÓN: CLOUDINARY

Cloudinary es un servicio gratuito de almacenamiento de imágenes en la nube.

**Plan Gratuito:**
- 25 GB de almacenamiento
- 25 GB de ancho de banda/mes
- Transformaciones de imágenes
- CDN global

---

## 📝 PASOS PARA CONFIGURAR:

### **1. Crear Cuenta en Cloudinary**

1. Ir a: https://cloudinary.com/users/register/free
2. Registrarse con email
3. Verificar email
4. Ir al Dashboard

### **2. Obtener Credenciales**

En el Dashboard de Cloudinary verás:

```
Cloud name: tu_cloud_name
API Key: 123456789012345
API Secret: abcdefghijklmnopqrstuvwxyz123
```

### **3. Configurar en Railway**

1. Ir a tu proyecto en Railway
2. Click en "Variables"
3. Agregar estas 3 variables:

```
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123
```

4. Click en "Deploy" para aplicar cambios

### **4. Instalar Dependencias**

Agregar a `requirements.txt`:

```
cloudinary==1.36.0
django-cloudinary-storage==0.3.0
```

### **5. Actualizar settings.py**

Agregar al final de `settings.py`:

```python
# Cloudinary Configuration
import cloudinary
import cloudinary.uploader
import cloudinary.api

if os.environ.get('CLOUDINARY_CLOUD_NAME'):
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True
    )
    
    # Usar Cloudinary para archivos media
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
```

### **6. Actualizar INSTALLED_APPS**

En `settings.py`, agregar a `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... otras apps
    'cloudinary_storage',
    'cloudinary',
    # ... resto de apps
]
```

**IMPORTANTE:** Agregar ANTES de `django.contrib.staticfiles`

---

## 🚀 DESPUÉS DE CONFIGURAR:

1. **Commit y push:**
   ```bash
   git add .
   git commit -m "FEAT: Configurar Cloudinary para almacenamiento persistente"
   git push
   ```

2. **Railway desplegará automáticamente**

3. **Capturar nueva foto:**
   - Las nuevas fotos se subirán a Cloudinary
   - Se verán en el admin
   - Persistirán entre deploys

---

## ✅ BENEFICIOS:

- ✅ Imágenes persisten entre deploys
- ✅ CDN global (carga rápida)
- ✅ Transformaciones automáticas (thumbnails)
- ✅ Backup automático
- ✅ Gratis hasta 25GB

---

## 🔍 VERIFICAR QUE FUNCIONA:

1. Capturar nueva foto desde el sidebar
2. Ir al admin: `/admin/attendance/securityphoto/`
3. Click en la foto
4. Deberías ver la imagen (URL de Cloudinary)

---

## 📊 FOTOS ANTIGUAS:

Las fotos capturadas ANTES de configurar Cloudinary:
- ❌ No se verán (archivos perdidos)
- ✅ Datos en BD siguen ahí
- ✅ GPS y metadata intactos

Las fotos DESPUÉS de configurar Cloudinary:
- ✅ Se verán siempre
- ✅ Persistentes
- ✅ Accesibles desde cualquier lugar

---

## 🆘 ALTERNATIVA TEMPORAL:

Si no quieres configurar Cloudinary ahora, puedes:

1. **Usar solo en local** (desarrollo)
2. **Configurar más tarde** (cuando vayas a producción)
3. **Las fotos se guardan en BD** (solo no se ven las imágenes)

---

## 📞 SOPORTE:

Si tienes problemas:
1. Verifica las credenciales en Railway
2. Revisa los logs: `railway logs`
3. Verifica que las variables estén bien escritas

---

**¿Quieres que configure Cloudinary ahora o lo dejamos para después?**
