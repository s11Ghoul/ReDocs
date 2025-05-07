from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Document, Reminder, EmailLog, HealthCheck


class ReminderInline(admin.TabularInline):
    """Встроенная форма для редактирования напоминаний"""
    model = Reminder
    extra = 1


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Document"""
    list_display = ['title', 'responsible_name', 'responsible_email', 'expiry_date', 'status_with_color', 'has_file']
    list_filter = ['status', 'expiry_date']
    search_fields = ['title', 'responsible_name', 'responsible_email', 'comments']
    date_hierarchy = 'expiry_date'
    inlines = [ReminderInline]

    fieldsets = (
        (_('Основная информация'), {
            'fields': ('title', 'received_date', 'expiry_date', 'status')
        }),
        (_('Контакты'), {
            'fields': ('responsible_name', 'responsible_email', 'additional_emails')
        }),
        (_('Дополнительно'), {
            'fields': ('document_file', 'comments')
        }),
    )

    def status_with_color(self, obj):
        """Отображение статуса документа с цветом"""
        colors = {
            'active': 'green',
            'expiring_soon': 'orange',
            'expired': 'red',
        }

        status_display = obj.get_status_display()
        color = colors.get(obj.status, 'black')

        return format_html('<span style="color: {};">{}</span>', color, status_display)
    status_with_color.short_description = _('Статус')

    def has_file(self, obj):
        """Отображает, есть ли у документа прикрепленный файл"""
        if obj.document_file:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_file.short_description = _('Файл')


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Reminder"""
    list_display = ['document', 'days_before_expiry', 'sent_date', 'is_sent']
    list_filter = ['sent_date']
    search_fields = ['document__title']

    def is_sent(self, obj):
        """Отображает, было ли отправлено напоминание"""
        if obj.sent_date:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    is_sent.short_description = _('Отправлено')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели EmailLog"""
    list_display = ['document', 'sent_at', 'recipients', 'status']
    list_filter = ['sent_at', 'status']
    search_fields = ['document__title', 'recipients', 'subject']
    date_hierarchy = 'sent_at'
    readonly_fields = ['document', 'reminder', 'recipients', 'subject', 'message', 'sent_at', 'status', 'error_message']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели HealthCheck"""
    list_display = ['check_date', 'status', 'reminders_checked', 'reminders_sent']
    list_filter = ['check_date', 'status']
    date_hierarchy = 'check_date'
    readonly_fields = ['check_date', 'status', 'reminders_checked', 'reminders_sent', 'error_message']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False