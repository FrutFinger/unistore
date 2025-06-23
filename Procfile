release: python manage.py migrate --noinput || echo "Migration failed, continuing..."
web: gunicorn config.wsgi 