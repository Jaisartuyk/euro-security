# 🛡️ EURO SECURITY - Sistema de Gestión Empresarial

**Sistema integral de gestión de recursos humanos y seguridad empresarial desarrollado con Django y tecnologías modernas.**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://djangoproject.com)
[![PWA](https://img.shields.io/badge/PWA-Ready-purple.svg)](https://web.dev/progressive-web-apps/)
[![GPS](https://img.shields.io/badge/GPS-Tracking-orange.svg)](https://developers.google.com/maps)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## 🏢 Descripción

Sistema completo de gestión de personal para empresas de seguridad física, desarrollado con Django. Permite administrar empleados, departamentos, puestos de trabajo y generar reportes detallados.

## ✨ Características Principales

### 🏢 Gestión de Departamentos
- ✅ Creación y administración de departamentos
- 💰 Control de presupuestos departamentales
- 👨‍💼 Asignación de jefes de departamento
- 📊 Estadísticas por departamento
- 🔄 Transferencias masivas de empleados

### 👥 Gestión de Empleados
- 📝 Registro completo de empleados
- 📋 Información personal y laboral detallada
- 📄 Gestión de documentos y certificaciones
- 🎓 Control de capacitaciones
- ⭐ Evaluaciones de desempeño
- 🔄 Transferencias entre departamentos

### 💼 Puestos de Trabajo
- 📋 Definición detallada de puestos
- 📝 Requisitos específicos por puesto
- 💰 Rangos salariales
- 📈 Niveles jerárquicos
- 📊 Control de vacantes disponibles

### 📊 Dashboard y Reportes
- 🎯 Dashboard interactivo con métricas
- 📈 Gráficos en tiempo real
- 🔔 Sistema de notificaciones
- 💰 Análisis salarial
- 📋 Reportes personalizables

### 🔐 Seguridad
- 🔒 Autenticación robusta
- 👥 Control de acceso por roles
- 📝 Auditoría de cambios
- 💾 Respaldos automáticos

## 🚀 Instalación Rápida

### Requisitos Previos
- Python 3.8+
- pip
- Virtualenv (recomendado)

### Pasos de Instalación

1. **Navegar al directorio del proyecto**
```bash
cd security_hr_system
```

2. **Crear entorno virtual**
```bash
python -m venv venv
```

3. **Activar entorno virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

5. **Configurar base de datos**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Ejecutar servidor**
```bash
python manage.py runserver
```

8. **Acceder a la aplicación**
- 🌐 Aplicación: http://127.0.0.1:8000
- ⚙️ Admin: http://127.0.0.1:8000/admin

## 📁 Estructura del Proyecto

```
security_hr_system/
├── 🏗️ security_hr_system/     # Configuración principal
├── 🎯 core/                   # Modelos base y utilidades
├── 📊 dashboard/              # Dashboard y estadísticas
├── 🏢 departments/            # Gestión de departamentos
├── 👥 employees/              # Gestión de empleados
├── 💼 positions/              # Gestión de puestos
├── 📋 reports/                # Sistema de reportes
├── 🎨 templates/              # Plantillas HTML
├── 📁 static/                 # Archivos estáticos
├── 📁 media/                  # Archivos subidos
└── 📄 requirements.txt        # Dependencias
```

## 🎯 Módulos Principales

### 📊 Dashboard
- Vista general del sistema
- Estadísticas en tiempo real
- Notificaciones importantes
- Acciones rápidas

### 🏢 Departamentos
- **Modelos**: Department, DepartmentBudget
- **Funciones**: CRUD, control presupuestario, estadísticas
- **Tipos**: RRHH, Sistemas, Operaciones, Administración, Seguridad, etc.

### 👥 Empleados
- **Modelos**: Employee, EmployeeDocument, EmployeeTraining, EmployeePerformanceReview
- **Funciones**: Gestión completa de personal, documentos, capacitaciones
- **Características especiales**: Transferencias masivas, evaluaciones de desempeño

### 💼 Puestos de Trabajo
- **Modelos**: Position, PositionRequirement, PositionHistory
- **Funciones**: Definición de puestos, requisitos, historial de cambios
- **Análisis**: Rangos salariales, demanda de puestos

## ⚙️ Configuración

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 🎨 Personalización

### Colores Corporativos
Los colores están definidos en `templates/base.html`:
```css
:root {
    --primary-color: #1e3a8a;    /* Azul principal */
    --secondary-color: #3b82f6;  /* Azul secundario */
    --accent-color: #06b6d4;     /* Azul acento */
}
```

## 🔧 Uso del Sistema

### Primer Uso
1. 👤 Acceder como superusuario
2. 🏢 Crear departamentos básicos
3. 💼 Definir puestos de trabajo
4. 👥 Registrar empleados
5. ⚙️ Configurar permisos de usuario

### Funcionalidades Clave

#### 🔄 Transferencias Masivas
- Acceder a "Empleados" > "Transferencia Masiva"
- Seleccionar departamento origen y destino
- Especificar fecha de transferencia
- Confirmar operación

#### 📄 Gestión de Documentos
- Subir documentos por empleado
- Control de vencimientos
- Verificación de documentos

#### ⭐ Evaluaciones de Desempeño
- Crear evaluaciones periódicas
- Calificaciones por categorías
- Seguimiento de objetivos

## 🔗 API Endpoints

### Estadísticas
- `/api/dashboard/stats/` - Estadísticas generales
- `/api/departamentos/estadisticas/` - Estadísticas de departamentos
- `/api/empleados/estadisticas/` - Estadísticas de empleados
- `/api/puestos/estadisticas/` - Estadísticas de puestos

## 🛠️ Mantenimiento

### Respaldos
```bash
# Respaldar base de datos
python manage.py dumpdata > backup.json

# Restaurar base de datos
python manage.py loaddata backup.json
```

## 📞 Soporte Técnico

### Problemas Comunes

1. **Error de migración**
   ```bash
   python manage.py makemigrations --empty app_name
   python manage.py migrate
   ```

2. **Archivos estáticos no cargan**
   ```bash
   python manage.py collectstatic
   ```

## 📄 Licencia

Este proyecto está desarrollado específicamente para **TV Services** y es de uso interno de la empresa.

---

**🛡️ TV Services - Sistema de Gestión de Personal**  
*Seguridad Física Profesional*

**Versión:** 1.0.0  
**Desarrollado con:** Django 4.2.7  
**Fecha:** 2024
