release: python manage.py debug_db && python manage.py setup_db
web: python manage.py migrate --noinput && gunicorn config.wsgi 