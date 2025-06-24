#!/bin/bash

echo "=== Starting application ==="
echo "Current directory: $(pwd)"
echo "Files in current directory: $(ls -la)"

# Создаем папку для медиа файлов
echo "=== Creating media directory ==="
mkdir -p /tmp/media
mkdir -p /tmp/media/products

# Ждем немного, чтобы база данных была готова
echo "Waiting for database to be ready..."
sleep 5

# Применяем миграции
echo "=== Applying migrations ==="
python manage.py migrate --verbosity=2

# Проверяем результат миграций
echo "=== Migration result: $? ==="

# Загружаем тестовые данные, если база пустая
echo "=== Loading sample data ==="
python manage.py load_sample_data

# Создаем суперпользователя если переменные окружения установлены
if [ ! -z "$DJANGO_SUPERUSER_USERNAME" ] && [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "=== Creating superuser ==="
    python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL
    echo "Superuser created successfully"
fi

# Запускаем сервер
echo "=== Starting server ==="
gunicorn config.wsgi 