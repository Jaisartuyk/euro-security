#!/bin/bash
# Script para ejecutar el comando de crear formularios de visitantes

echo "🚀 Ejecutando creación de formularios de visitantes..."
python manage.py create_visitor_forms

echo "✅ Comando ejecutado. Iniciando servidor..."
python manage.py runserver 0.0.0.0:$PORT
