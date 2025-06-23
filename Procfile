release: python manage.py migrate --verbosity=2 && python manage.py collectstatic --noinput || echo "Setup failed, continuing..."
web: gunicorn config.wsgi 