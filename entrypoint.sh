#!/bin/bash

echo "=== Starting application ==="
echo "Current directory: $(pwd)"
echo "Files in current directory: $(ls -la)"

# Ждем немного, чтобы база данных была готова
echo "Waiting for database to be ready..."
sleep 5

# Применяем миграции
echo "=== Applying migrations ==="
python manage.py migrate --verbosity=2

# Проверяем результат миграций
echo "=== Migration result: $? ==="

# Запускаем сервер
echo "=== Starting server ==="
gunicorn config.wsgi 