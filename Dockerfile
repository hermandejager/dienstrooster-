# Minimal production-ish Dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Expose default Flask port
EXPOSE 5000
# Use environment SECRET_KEY and ADMIN_PASSWORD from runtime
ENV FLASK_ENV=production \
    GUNICORN_WORKERS=3 \
    GUNICORN_TIMEOUT=60
# Production server via gunicorn
CMD ["gunicorn", "-w", "${GUNICORN_WORKERS}", "-b", "0.0.0.0:5000", "app:app", "--timeout", "${GUNICORN_TIMEOUT}"]
