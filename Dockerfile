FROM python:3.11-slim

# Use key=value style to avoid warnings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System packages if you need to build wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy the rest of the app
COPY . /app

EXPOSE 8000
# Use gunicorn for production, not runserver
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]