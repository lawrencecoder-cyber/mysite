#!/usr/bin/env bash
set -o errexit  # stop on any error

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir

echo "🗄️ Applying database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🔍 Running Django deployment checks..."
python manage.py check --deploy

echo "✅ Build completed successfully!"
