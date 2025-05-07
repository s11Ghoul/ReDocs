from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from datetime import timedelta
import logging

from .models import Document, Reminder, EmailLog, HealthCheck

logger = logging.getLogger(__name__)

@shared_task
def check_document_reminders():
    """
    Проверка всех документов и отправка напоминаний,
    если подходит срок отправки напоминания.
    """
    logger.info("Начата проверка напоминаний о документах")

    today = timezone.now().date()
    checked_count = 0
    sent_count = 0
    errors = []

    # Получаем все активные документы, кроме просроченных
    documents = Document.objects.exclude(status='expired')

    for document in documents:
        # Проверяем все напоминания для документа
        reminders = Reminder.objects.filter(document=document)

        for reminder in reminders:
            checked_count += 1

            # Если напоминание должно быть отправлено сегодня
            if reminder.should_send_today():
                try:
                    send_document_reminder(document, reminder)

                    # Отмечаем напоминание как отправленное
                    reminder.sent_date = timezone.now()
                    reminder.save()

                    sent_count += 1
                    logger.info(f"Напоминание о документе '{document.title}' отправлено ({reminder.days_before_expiry} дней)")

                except Exception as e:
                    error_msg = f"Ошибка при отправке напоминания о документе '{document.title}': {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

    # Логируем результаты
    if errors:
        error_message = "\n".join(errors)
        logger.error(f"Завершена проверка напоминаний. Проверено: {checked_count}, отправлено: {sent_count}, ошибок: {len(errors)}")
    else:
        error_message = ""
        logger.info(f"Завершена проверка напоминаний. Проверено: {checked_count}, отправлено: {sent_count}, ошибок: 0")

    # Возвращаем результаты для использования в health_check
    return {
        'checked': checked_count,
        'sent': sent_count,
        'errors': error_message
    }


def send_document_reminder(document, reminder):
    """
    Отправка напоминания о документе по email
    """
    # Получаем список всех получателей
    recipients = document.get_recipient_emails()

    # Формируем заголовок письма
    days_left = (document.expiry_date - timezone.now().date()).days

    if days_left < 0:
        subject = f"ВНИМАНИЕ! Документ '{document.title}' просрочен"
    else:
        subject = f"Напоминание: документ '{document.title}' истекает через {days_left} дней"

    # Формируем текст письма
    context = {
        'document': document,
        'days_left': days_left,
        'days_before_expiry': reminder.days_before_expiry,
        'expiry_date': document.expiry_date.strftime('%d.%m.%Y'),
    }

    message = render_to_string('documents/email/document_reminder.txt', context)
    html_message = render_to_string('documents/email/document_reminder.html', context)

    # Создаем объект EmailMessage для возможности прикрепления файла
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )

    # Если есть HTML версия, добавляем её
    email.content_subtype = "html"
    email.body = html_message

    # Если к документу прикреплен файл, добавляем его к письму
    if document.document_file:
        email.attach_file(document.document_file.path)

    # Отправляем письмо
    sent = email.send()

    # Логируем результат отправки
    status = "sent" if sent else "failed"

    EmailLog.objects.create(
        document=document,
        reminder=reminder,
        recipients=", ".join(recipients),
        subject=subject,
        message=html_message,
        status=status,
        error_message="" if sent else "Ошибка при отправке email"
    )

    return sent


@shared_task
def run_health_check():
    """
    Проверка работоспособности системы и отправка отчета администратору
    """
    logger.info("Начата проверка работоспособности системы")

    try:
        # Получаем результаты проверки напоминаний за последние 24 часа
        last_24h = timezone.now() - timedelta(hours=24)

        # Проверяем логи отправки напоминаний
        email_logs = EmailLog.objects.filter(sent_at__gte=last_24h)
        reminders_sent = email_logs.count()
        failed_emails = email_logs.filter(status='failed').count()

        # Проверяем логи предыдущих health-check
        last_check = HealthCheck.objects.order_by('-check_date').first()

        # Собираем информацию о статусе системы
        status = "ok"
        error_message = ""

        if failed_emails > 0:
            status = "warning"
            error_message += f"Не удалось отправить {failed_emails} email-уведомлений.\n"

        if last_check and (timezone.now() - last_check.check_date) > timedelta(hours=30):
            status = "error"
            error_message += "Система проверки работоспособности не запускалась более 30 часов.\n"

        # Сохраняем результаты проверки
        health_check = HealthCheck.objects.create(
            status=status,
            reminders_checked=0,  # Будет обновлено после запуска задачи
            reminders_sent=reminders_sent,
            error_message=error_message
        )

        # Отправляем email администратору с результатами проверки
        send_health_check_report(health_check)

        logger.info(f"Проверка работоспособности завершена. Статус: {status}")

        # Запускаем проверку напоминаний для обновления счетчиков
        reminders_result = check_document_reminders.delay()
        reminders_result.get()  # Ждем завершения задачи

        return {
            'status': status,
            'reminders_sent': reminders_sent,
            'errors': error_message
        }

    except Exception as e:
        logger.error(f"Ошибка при проверке работоспособности: {str(e)}")

        # Создаем запись о проверке с ошибкой
        HealthCheck.objects.create(
            status="error",
            reminders_checked=0,
            reminders_sent=0,
            error_message=str(e)
        )

        return {
            'status': 'error',
            'reminders_sent': 0,
            'errors': str(e)
        }


def send_health_check_report(health_check):
    """
    Отправка отчета о работоспособности системы администратору
    """
    subject = f"Re:Docs Health Check - {health_check.check_date.strftime('%d.%m.%Y %H:%M')}"

    if health_check.status == 'ok':
        subject += " [OK]"
    elif health_check.status == 'warning':
        subject += " [WARNING]"
    else:
        subject += " [ERROR]"

    # Формируем текст письма
    context = {
        'health_check': health_check,
        'check_date': health_check.check_date.strftime('%d.%m.%Y %H:%M'),
    }

    message = render_to_string('documents/email/health_check.txt', context)
    html_message = render_to_string('documents/email/health_check.html', context)

    # Отправляем email администратору
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message,
        fail_silently=True,
    )