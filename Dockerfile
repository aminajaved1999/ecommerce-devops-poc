FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Copy and make the entrypoint script executable
# This is the line that was fixed (typo corrected)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Start the app using the entrypoint script
# This is the line that was fixed (typo corrected)
CMD ["/app/entrypoint.sh"]