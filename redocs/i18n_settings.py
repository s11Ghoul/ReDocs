from django.utils.translation import gettext_lazy as _

# Настройки локализации
LANGUAGES = [
    ('uk', _('Українська')),  # Украинский
    ('ru', _('Русский')),     # Русский
    ('en', _('English')),     # Английский
]

# Пути к файлам переводов
LOCALE_PATHS = [
    'locale/',
]

# Ключевые строки для перевода
TRANSLATABLE_STRINGS = {
    'site_name': _('Re:Docs'),
    'site_description': _('Система управления документами'),

    # Документы
    'document': _('Документ'),
    'documents': _('Документы'),
    'active_documents': _('Действительные документы'),
    'expiring_soon_documents': _('Документы, срок которых скоро истекает'),
    'expired_documents': _('Просроченные документы'),
    'document_title': _('Название документа'),
    'received_date': _('Дата получения'),
    'expiry_date': _('Дата окончания'),
    'responsible': _('Ответственный'),
    'responsible_email': _('Email ответственного'),
    'additional_emails': _('Дополнительные email адреса'),
    'document_file': _('Файл документа'),
    'comments': _('Комментарии'),
    'status': _('Статус'),
    'add_document': _('Добавить документ'),
    'edit_document': _('Редактировать документ'),
    'delete_document': _('Удалить документ'),

    # Статусы
    'active': _('Действителен'),
    'expiring_soon': _('Скоро истекает'),
    'expired': _('Просрочен'),

    # Напоминания
    'reminders': _('Напоминания'),
    'reminder': _('Напоминание'),
    'days_before_expiry': _('Дней до окончания'),
    'sent_date': _('Дата отправки'),
    'reminder_settings': _('Настройки напоминаний'),
    'send_reminders': _('Отправить напоминания'),

    # Логи
    'logs': _('Журнал событий'),
    'email_logs': _('Журнал отправки уведомлений'),
    'health_checks': _('Проверки работоспособности'),
    'status_ok': _('Система работает нормально'),
    'status_warning': _('Предупреждение'),
    'status_error': _('Ошибка'),

    # Действия
    'save': _('Сохранить'),
    'cancel': _('Отмена'),
    'confirm': _('Подтвердить'),
    'back': _('Назад'),
    'view': _('Просмотр'),
    'edit': _('Редактировать'),
    'delete': _('Удалить'),
    'download': _('Скачать'),

    # Авторизация
    'login': _('Вход'),
    'logout': _('Выход'),
    'username': _('Имя пользователя'),
    'password': _('Пароль'),
    'change_password': _('Изменить пароль'),

    # Сообщения
    'document_created': _('Документ успешно создан.'),
    'document_updated': _('Документ успешно обновлен.'),
    'document_deleted': _('Документ успешно удален.'),
    'password_changed': _('Пароль успешно изменен.'),

    # Прочее
    'dashboard': _('Панель управления'),
    'total': _('Всего'),
    'search': _('Поиск'),
    'apply_filters': _('Применить фильтры'),
    'reset_filters': _('Сбросить фильтры'),
    'no_documents': _('Документы не найдены'),
    'no_logs': _('Логи не найдены'),
    'file_size_limit': _('Максимальный размер файла: 10 МБ'),
    'allowed_file_formats': _('Допустимые форматы файлов: PDF, JPG'),
}