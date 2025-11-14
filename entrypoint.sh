# entrypoint.sh

#!/bin/sh

# REMOVED: # Apply database migrations (to prevent unnecessary work/errors)
# REMOVED: # python manage.py migrate

# Collect static files (CRITICAL NEW STEP)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:8000