# --- Base image ---
FROM python:3.11-slim

# --- Environment variables ---
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# --- Set work directory ---
WORKDIR /app

# --- Install system dependencies ---
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Install Python dependencies ---
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy project ---
COPY . /app/

# --- Collect static files (safe for production) ---
RUN python manage.py collectstatic --noinput || true

# --- Expose port Fly expects ---
EXPOSE 8080

# --- Run with Gunicorn (production server) ---
CMD ["gunicorn", "mysite.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120"]
