FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Copy and make the entrypoint script executable
COPY entrypoint.sh /app/entrylpoint.sh
RUN chmod +x /app/entrylpoint.sh

# Start the app using the entrypoint script
CMD ["/app/entrylpoint.sh"]