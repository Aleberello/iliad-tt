#!/bin/bash

if [ "$DEBUG" == "true" ]; then
    echo "Creating Migrations..."
    python manage.py makemigrations
    echo ====================================
fi

echo "Starting Migrations..."
until python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done
echo ====================================

echo "Starting Collectstatic..."
python manage.py collectstatic --noinput
echo ====================================

echo "Starting Development Server..."
python manage.py runserver 0.0.0.0:8000

exec "$@"