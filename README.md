# ClotheShop - Магазин одежды

Веб-приложение для интернет-магазина одежды, созданное на Django.

## 🚀 Возможности

- Каталог товаров с фильтрацией
- Корзина покупок
- Система заказов
- Админ-панель для управления товарами
- Контактная форма
- Избранные товары
- Адаптивный дизайн

## 🛠️ Технологии

- **Backend**: Django 5.0.4
- **Database**: PostgreSQL (продакшен), SQLite (разработка)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Railway

## 📦 Установка

### Локальная разработка

1. Клонируйте репозиторий:
```bash
git clone <your-repo-url>
cd clotheshop
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Примените миграции:
```bash
python manage.py migrate
```

5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

6. Запустите сервер:
```bash
python manage.py runserver
```

Сайт будет доступен по адресу: http://127.0.0.1:8000/

## 🌐 Деплой на Railway

1. Зарегистрируйтесь на [Railway](https://railway.app/)
2. Подключите ваш GitHub репозиторий
3. Railway автоматически определит Django проект и настроит деплой
4. Добавьте переменные окружения в Railway:
   - `SECRET_KEY` - секретный ключ Django
   - `DEBUG` - False для продакшена
   - `ALLOWED_HOSTS` - ваш домен Railway

## 📁 Структура проекта

```
clotheshop/
├── clotheshop/          # Основное приложение
│   ├── models.py       # Модели данных
│   ├── views.py        # Представления
│   ├── forms.py        # Формы
│   ├── admin.py        # Админ-панель
│   ├── static/         # Статические файлы
│   └── templates/      # Шаблоны
├── config/             # Настройки проекта
├── media/              # Загруженные файлы
├── staticfiles/        # Собранные статические файлы
└── manage.py           # Управление Django
```

## 🔧 Администрирование

Доступ к админ-панели: `/admin/`

Возможности:
- Управление товарами и их размерами
- Просмотр заказов
- Управление сообщениями
- Просмотр избранных товаров

## 📝 Лицензия

Этот проект создан в образовательных целях. 