# 📋 EJECUTAR FORMULARIOS DE VISITANTES EN PRODUCCIÓN

## 🎯 FORMULARIOS A CREAR:

### 1. **REGISTRO DE VISITANTES URBANIZACIÓN** (OPA-EUEC-12)
- Control de ingreso y salida de visitantes
- 8 campos configurados
- No requiere aprobación

### 2. **REGISTRO TOMA DE CONOCIMIENTO** (OPA-EUEC-08)
- Registro de capacitaciones del personal
- 9 campos con firma digital
- Requiere aprobación

---

## 🚀 INSTRUCCIONES PARA EJECUTAR:

### **OPCIÓN 1: Desde Railway Dashboard**

1. Ve a: https://railway.app/
2. Selecciona tu proyecto: `euro-security-production`
3. Ve a la pestaña **"Settings"**
4. Busca la sección **"Deploy"**
5. En **"Custom Start Command"** ejecuta temporalmente:
   ```bash
   python manage.py create_visitor_forms && python manage.py runserver
   ```
6. O ve a **"Variables"** y ejecuta en la consola de Railway

### **OPCIÓN 2: Desde Railway CLI (si tienes instalado)**

```bash
railway run python manage.py create_visitor_forms
```

### **OPCIÓN 3: Desde el Admin de Django**

1. Ve a: https://euro-security-production.up.railway.app/admin/
2. Inicia sesión como superusuario
3. Ve a **"Django Shell"** (si está disponible)
4. Ejecuta:
   ```python
   from django.core.management import call_command
   call_command('create_visitor_forms')
   ```

### **OPCIÓN 4: Crear manualmente desde Admin**

1. Ve a: https://euro-security-production.up.railway.app/admin/forms/formtemplate/
2. Haz clic en **"Add Form Template"**
3. Crea cada formulario con los datos especificados

---

## ✅ VERIFICAR QUE SE CREARON:

1. Ve a: https://euro-security-production.up.railway.app/formularios/
2. Deberías ver los 2 nuevos formularios en la categoría **"Operaciones de Seguridad"**:
   - ✅ Registro de Visitantes Urbanización (OPA-EUEC-12)
   - ✅ Registro Toma de Conocimiento (OPA-EUEC-08)

---

## 📊 DETALLES DE LOS FORMULARIOS:

### **REGISTRO DE VISITANTES** (OPA-EUEC-12)
```
Campos:
1. Fecha (date)
2. Nombres (text)
3. Apellidos (text)
4. RCI/Cédula (text)
5. M/Escolar (text, opcional)
6. Propietario (text)
7. N. Inmueble (text)
8. H. Salida (text, opcional)
```

### **REGISTRO TOMA DE CONOCIMIENTO** (OPA-EUEC-08)
```
Sección 1: Información General
- Área (text)
- Fecha (date)
- Capacitador (text)
- Tema Tratado (textarea)

Sección 2: Datos del Personal
- Nombres (text)
- Apellidos (text)
- Cédula (text)
- Firma (signature)
- Cargo (text)
```

---

## 🔧 SI HAY PROBLEMAS:

Si el comando no se ejecuta correctamente, puedes crear los formularios manualmente desde el admin de Django siguiendo la estructura especificada arriba.

---

## 📝 NOTAS:

- Los formularios se crean con la categoría **"Operaciones de Seguridad"**
- Ambos formularios están activos por defecto
- El formulario de visitantes NO requiere aprobación
- El formulario de toma de conocimiento SÍ requiere aprobación
- Ambos permiten guardar borradores

---

**¿Necesitas ayuda?** Contacta al equipo de desarrollo.
