FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies and dos2unix tool for line ending conversion
COPY requirements.txt .
RUN apt-get update && \
    apt-get install -y dos2unix && \
    pip install -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

COPY . .

# Copy and make the entrypoint script executable
COPY entrypoint.sh /app/entrypoint.sh

# FIX: Convert Windows (CRLF) line endings to Unix (LF) format
RUN dos2unix /app/entrypoint.sh

# Make executable (already in place, kept for clarity)
RUN chmod +x /app/entrypoint.sh

# Start the app using the entrypoint script
CMD ["/app/entrypoint.sh"]