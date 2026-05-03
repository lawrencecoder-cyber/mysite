#!/bin/bash

echo "Starting service: $SERVICE_TYPE"

if [ "$SERVICE_TYPE" = "web" ]; then
    python manage.py migrate
    gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT

elif [ "$SERVICE_TYPE" = "worker" ]; then
    celery -A mysite worker --loglevel=info

elif [ "$SERVICE_TYPE" = "beat" ]; then
    celery -A mysite beat --loglevel=info

else
    echo "Unknown SERVICE_TYPE"
fi
