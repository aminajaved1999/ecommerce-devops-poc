#!/bin/sh

# Collect static files (CRITICAL NEW STEP)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# NEW: Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000