from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction
import os

from .models import Document, Reminder, EmailLog, HealthCheck


@receiver(pre_save, sender=Document)
def update_document_status(sender, instance, **kwargs):
    """Обновление статуса документа перед сохранением"""
    today = timezone.now().date()
    days_until_expiry = (instance.expiry_date - today).days

    if days_until_expiry < 0:
        instance.status = 'expired'
    elif days_until_expiry <= 30:
        instance.status = 'expiring_soon'
    else:
        instance.status = 'active'


@receiver(post_save, sender=Document)
def handle_document_file(sender, instance, created, **kwargs):
    """Обработка прикрепленного файла документа"""
    # Если файл был заменен, удаляем старый файл
    if not created and hasattr(instance, '_old_document_file'):
        if instance._old_document_file and instance._old_document_file != instance.document_file:
            # Удаляем старый файл, если он был заменен
            if os.path.isfile(instance._old_document_file.path):
                os.remove(instance._old_document_file.path)


@receiver(pre_save, sender=Document)
def save_old_document_file(sender, instance, **kwargs):
    """Сохраняем данные о старом файле перед обновлением документа"""
    # Сохраняем старый файл для последующего сравнения
    if instance.pk:
        try:
            old_instance = Document.objects.get(pk=instance.pk)
            instance._old_document_file = old_instance.document_file
        except Document.DoesNotExist:
            pass


@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    """Удаление файла документа при удалении записи"""
    if instance.document_file:
        if os.path.isfile(instance.document_file.path):
            os.remove(instance.document_file.path)


@receiver(post_save, sender=Reminder)
def update_reminder_status(sender, instance, created, **kwargs):
    """Обновление статуса напоминания при его создании или изменении"""
    if created:
        # Проверяем, нужно ли отправить напоминание сразу после создания
        if instance.should_send_today():
            # Запускаем отправку уведомления в фоновом режиме
            from .tasks import send_document_reminder
            transaction.on_commit(lambda: send_document_reminder.delay(instance.document.id, instance.id))


@receiver(post_save, sender=EmailLog)
def notify_admin_on_error(sender, instance, created, **kwargs):
    """Отправка уведомления администратору при ошибке отправки email"""
    if created and instance.status == 'failed':
        # Добавляем запись в лог ошибок или отправляем уведомление администратору
        from .tasks import send_health_check_report
        transaction.on_commit(lambda: send_health_check_report.delay())