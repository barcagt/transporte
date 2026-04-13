#!/bin/bash
set -e  # Detener si hay error

echo "Ejecutando migraciones..."
python manage.py migrate

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando Gunicorn..."
gunicorn config.wsgi
