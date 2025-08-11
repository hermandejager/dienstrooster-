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
# Use environment SECRET_KEY and ADMIN_PASSWORD from runtime (e.g. docker run -e ...)
ENV FLASK_ENV=production
CMD ["python", "app.py"]
