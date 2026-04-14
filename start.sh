#!/bin/bash

echo "Starting application..."

# Wait for database to be ready (simple approach)
echo "Checking database connection..."
for i in {1..10}; do
    if python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings'); import django; django.setup(); from django.db import connection; connection.ensure_connection()" 2>/dev/null; then
        echo "Database connection successful!"
        break
    fi
    echo "Waiting for database... attempt $i/10"
    sleep 3
done

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Start the application
echo "Starting gunicorn..."
exec gunicorn config.wsgi --bind 0.0.0.0:$PORT