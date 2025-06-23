# Деплой на Railway

## Настройка переменных окружения

В Railway Dashboard нужно настроить следующие переменные окружения:

### Обязательные переменные:
- `DATABASE_URL`: `postgresql://postgres:tYIyjQVcRBDctRZtjxDRZQEzHvTvibgd@postgres.railway.internal:5432/railway`
- `SECRET_KEY`: Сгенерируйте новый секретный ключ Django
- `DEBUG`: `False` (для продакшена)
- `ALLOWED_HOSTS`: Ваш домен Railway (например: `your-app-name.railway.app`)

### Дополнительные переменные:
- `CSRF_TRUSTED_ORIGINS`: `https://your-app-name.railway.app`

## Команды для деплоя

После настройки переменных окружения, Railway автоматически выполнит следующие команды:

1. `pip install -r requirements.txt`
2. `python manage.py collectstatic --noinput`
3. `python manage.py migrate`
4. `gunicorn config.wsgi`

## Локальная разработка

Для локальной разработки используйте:

```bash
python manage.py runserver
```

## Проверка деплоя

После деплоя проверьте:
1. Главная страница загружается
2. Админ панель работает
3. Статические файлы загружаются
4. База данных работает

## Устранение проблем

Если возникают ошибки:
1. Проверьте переменные окружения в Railway Dashboard
2. Проверьте логи в Railway
3. Убедитесь, что все зависимости установлены
4. Проверьте, что миграции выполнены 