#!/bin/bash

# Script de inicio para Railway - Euro Security
# Ejecuta migraciones y collectstatic antes de iniciar el servidor

echo "🚀 Iniciando Euro Security HR System..."

# Instalar dependencias del sistema para OpenCV
echo "📦 Instalando dependencias del sistema..."
apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 || echo "⚠️ No se pudieron instalar dependencias del sistema (normal en algunos entornos)"

# Aplicar migraciones
echo "📦 Aplicando migraciones de base de datos..."
python manage.py migrate --noinput

# Verificar si la migración 0011 se aplicó
echo "🔍 Verificando migración 0011_add_security_ai_models..."
python manage.py showmigrations attendance | grep "0011_add_security_ai_models"

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar servidor Gunicorn
echo "✅ Iniciando servidor Gunicorn..."
exec gunicorn security_hr_system.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
