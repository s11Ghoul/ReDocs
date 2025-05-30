# Re:Docs - Система управления документами

Re:Docs - это веб-приложение для учёта документов с гибкой системой напоминаний об окончании срока действия, возможностью прикреплять файлы и уведомлять нескольких получателей по email.

## Основные возможности

- Учет документов и сроков их действия
- Гибкая система напоминаний по email
- Поддержка прикрепления файлов (PDF, JPG)
- Многоязычный интерфейс (украинский, русский, английский)
- Система аутентификации пользователей
- Панель управления с ключевыми показателями
- Журнал логов событий и уведомлений
- Ежедневная проверка работоспособности (health-check)

## Технологический стек

- **Backend**: Python + Django
- **Frontend**: Django Templates + Bootstrap 5
- **База данных**: SQLite (для разработки), PostgreSQL (для продакшена)
- **Фоновые задачи**: Celery + Redis
- **Отправка email**: SMTP
- **Локализация**: Django i18n

## Установка и запуск

### Требования

- Python 3.8 или выше
- Redis (для Celery)
- PostgreSQL (опционально, для продакшена)

### Шаги установки

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/redocs.git
cd redocs
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте переменные окружения в файле `.env`:
```bash
cp .env.example .env
# Отредактируйте .env файл, указав ваши настройки
```

5. Примените миграции базы данных:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер для разработки:
```bash
python manage.py runserver
```

8. Запустите Celery для обработки фоновых задач:
```bash
celery -A redocs worker -l info
```

9. Запустите планировщик Celery Beat:
```bash
celery -A redocs beat -l info
```

## Деплой в продакшен

### Настройки для облачного хостинга

1. Обновите файл `.env`:
    - Установите `DEBUG=False`
    - Укажите правильный `ALLOWED_HOSTS`
    - Настройте подключение к PostgreSQL
    - Настройте SMTP для отправки email

2. Соберите статические файлы:
```bash
python manage.py collectstatic
```

3. Настройте веб-сервер (Nginx, Apache) для обслуживания Django-приложения.

4. Настройте Gunicorn или uWSGI для запуска Django.

5. Настройте Supervisor для управления процессами Celery.

## Структура проекта

- `redocs/` - основной пакет Django проекта
- `documents/` - приложение для управления документами
- `templates/` - HTML шаблоны
- `static/` - статические файлы (CSS, JS)
- `media/` - загружаемые пользователями файлы

## Лицензия

MIT