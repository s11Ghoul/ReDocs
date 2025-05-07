#!/bin/bash

# Скрипт для запуска проекта Re:Docs в режиме разработки

# Проверка наличия виртуального окружения
if [ ! -d "venv" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
echo "Установка зависимостей..."
pip install -r requirements.txt

# Применение миграций
echo "Применение миграций..."
python manage.py migrate

# Сбор статических файлов
echo "Сбор статических файлов..."
python manage.py collectstatic --no-input

# Создание суперпользователя, если его нет
echo "Проверка наличия суперпользователя..."
python manage.py shell -c "from django.contrib.auth.models import User; print('Суперпользователь уже существует') if User.objects.filter(is_superuser=True).exists() else exit(1)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Создание суперпользователя..."
    python manage.py createsuperuser
fi

# Запуск Redis, если он установлен
if command -v redis-server >/dev/null 2>&1; then
    echo "Запуск Redis..."
    redis-server --daemonize yes
else
    echo "Redis не установлен. Установите Redis для использования Celery."
fi

# Запуск Celery worker
echo "Запуск Celery worker..."
celery -A redocs worker --loglevel=info --detach

# Запуск Celery beat
echo "Запуск Celery beat..."
celery -A redocs beat --loglevel=info --detach

# Запуск сервера разработки Django
echo "Запуск сервера разработки Django..."
python manage.py runserver 0.0.0.0:8000