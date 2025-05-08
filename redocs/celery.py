import os
from celery import Celery
from celery.schedules import crontab

# Устанавливаем переменную окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'redocs.settings')

app = Celery('redocs')

# Используем настройки Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим и регистрируем задачи из всех приложений
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'check-document-reminders-daily': {
        'task': 'documents.tasks.check_document_reminders',
        'schedule': crontab(hour=4, minute=0),  # Запуск каждый день в 4:00 утра
    },
    'run-health-check-daily': {
        'task': 'documents.tasks.run_health_check',
        'schedule': crontab(hour=5, minute=0),  # Запуск каждый день в 5:00 утра
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

app.conf.beat_schedule = {
    'check-document-reminders-daily': {
        'task': 'documents.tasks.check_document_reminders',
        'schedule': crontab(hour=4, minute=0),
    },
    'run-health-check-daily': {
        'task': 'documents.tasks.run_health_check',
        'schedule': crontab(hour=5, minute=0),
    },
    # Добавляем новую задачу
    'update-document-statuses': {
        'task': 'documents.tasks.update_document_statuses',
        'schedule': crontab(minute=0),  # Каждый час в начале часа
    },
}