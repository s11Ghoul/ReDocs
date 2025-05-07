from django.db import models
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import os

def document_file_path(instance, filename):
    """Функция для определения пути сохранения файла документа"""
    # Создаем путь вида: documents/[id]/[filename]
    return os.path.join('documents', str(instance.id), filename)

class Document(models.Model):
    """Модель для хранения информации о документе"""

    STATUS_CHOICES = (
        ('active', 'Действителен'),
        ('expiring_soon', 'Скоро истекает'),
        ('expired', 'Просрочен'),
    )

    title = models.CharField(max_length=255, verbose_name="Название")
    received_date = models.DateField(verbose_name="Дата получения")
    expiry_date = models.DateField(verbose_name="Дата окончания")
    responsible_name = models.CharField(max_length=255, verbose_name="Ответственный (ФИО)")
    responsible_email = models.EmailField(verbose_name="Email ответственного")
    additional_emails = models.TextField(blank=True, verbose_name="Дополнительные email адреса")
    document_file = models.FileField(upload_to=document_file_path, verbose_name="Файл документа", null=True, blank=True)
    comments = models.TextField(blank=True, verbose_name="Комментарий / описание")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def clean(self):
        """Валидация дополнительных email адресов"""
        if self.additional_emails:
            emails = [email.strip() for email in self.additional_emails.split(',')]
            for email in emails:
                try:
                    validate_email(email)
                except ValidationError:
                    raise ValidationError({'additional_emails': f'Email адрес "{email}" некорректен'})

    def save(self, *args, **kwargs):
        """Переопределение сохранения для обновления статуса"""
        today = timezone.now().date()
        days_until_expiry = (self.expiry_date - today).days

        # Обновление статуса в зависимости от срока до окончания
        if days_until_expiry < 0:
            self.status = 'expired'
        elif days_until_expiry <= 30:  # Скоро истекает если <= 30 дней
            self.status = 'expiring_soon'
        else:
            self.status = 'active'

        super().save(*args, **kwargs)

    def get_recipient_emails(self):
        """Получение всех email адресов для уведомлений"""
        emails = [self.responsible_email]

        if self.additional_emails:
            additional = [email.strip() for email in self.additional_emails.split(',')]
            emails.extend(additional)

        return emails

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['expiry_date']  # Сортировка по дате окончания


class Reminder(models.Model):
    """Модель для хранения настроек напоминаний о документах"""

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='reminders', verbose_name="Документ")
    days_before_expiry = models.PositiveIntegerField(verbose_name="Дней до окончания для напоминания")
    sent_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата отправки напоминания")

    def is_sent(self):
        """Проверка, было ли отправлено напоминание"""
        return self.sent_date is not None

    def should_send_today(self):
        """Проверка, должно ли напоминание быть отправлено сегодня"""
        if self.is_sent():
            return False

        today = timezone.now().date()
        target_date = self.document.expiry_date - timezone.timedelta(days=self.days_before_expiry)

        return target_date == today

    def __str__(self):
        return f"Напоминание за {self.days_before_expiry} дней до окончания документа '{self.document}'"

    class Meta:
        verbose_name = "Напоминание"
        verbose_name_plural = "Напоминания"
        ordering = ['days_before_expiry']
        unique_together = ['document', 'days_before_expiry']  # Запрет дублирования периодов для одного документа


class EmailLog(models.Model):
    """Модель для логирования отправленных email уведомлений"""

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='email_logs', verbose_name="Документ")
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name='email_logs', verbose_name="Напоминание")
    recipients = models.TextField(verbose_name="Получатели")
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    message = models.TextField(verbose_name="Текст письма")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    status = models.CharField(max_length=50, verbose_name="Статус отправки")
    error_message = models.TextField(blank=True, verbose_name="Текст ошибки")

    def __str__(self):
        return f"Email для '{self.document}' от {self.sent_at.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "Лог email"
        verbose_name_plural = "Логи email"
        ordering = ['-sent_at']


class HealthCheck(models.Model):
    """Модель для логирования проверок работоспособности системы"""

    check_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата проверки")
    status = models.CharField(max_length=50, verbose_name="Статус")
    reminders_checked = models.PositiveIntegerField(default=0, verbose_name="Проверено напоминаний")
    reminders_sent = models.PositiveIntegerField(default=0, verbose_name="Отправлено напоминаний")
    error_message = models.TextField(blank=True, verbose_name="Текст ошибки")

    def __str__(self):
        return f"Проверка от {self.check_date.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "Проверка работоспособности"
        verbose_name_plural = "Проверки работоспособности"
        ordering = ['-check_date']