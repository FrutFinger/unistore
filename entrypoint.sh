#!/bin/bash

echo "Starting application..."

# Ждем немного, чтобы база данных была готова
sleep 5

# Применяем миграции
echo "Applying migrations..."
python manage.py migrate --noinput

# Запускаем сервер
echo "Starting server..."
gunicorn config.wsgi 