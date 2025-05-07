from django import forms
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Document, Reminder

class DocumentForm(forms.ModelForm):
    """Форма для создания и редактирования документа"""

    # Поле для выбора стандартных периодов напоминаний через чекбоксы
    reminder_periods = forms.MultipleChoiceField(
        choices=[
            (365, _('За 1 год')),
            (180, _('За 6 месяцев')),
            (90, _('За 3 месяца')),
            (30, _('За 1 месяц')),
            (14, _('За 2 недели')),
            (7, _('За 1 неделю')),
            (3, _('За 3 дня')),
            (1, _('За 1 день')),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Отправить напоминания')
    )

    # Поле для настройки пользовательского периода напоминания
    custom_reminder_period = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=365 * 5,  # Максимум 5 лет
        label=_('Другой период напоминания (в днях)')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Если редактируем существующий документ
        if self.instance.pk:
            # Заполняем поле reminder_periods значениями из БД
            existing_reminders = self.instance.reminders.values_list('days_before_expiry', flat=True)

            # Выбираем стандартные периоды из списка существующих напоминаний
            standard_periods = []
            for choice, _ in self.fields['reminder_periods'].choices:
                if choice in existing_reminders:
                    standard_periods.append(str(choice))

            # Заполняем значением пользовательского периода, если такой есть
            custom_periods = [period for period in existing_reminders
                              if period not in [choice[0] for choice in self.fields['reminder_periods'].choices]]

            if custom_periods:
                self.fields['custom_reminder_period'].initial = custom_periods[0]

            self.fields['reminder_periods'].initial = standard_periods

    def clean_document_file(self):
        """Проверка размера и типа загруженного файла"""
        document_file = self.cleaned_data.get('document_file')

        if document_file:
            # Проверка размера файла
            if document_file.size > settings.MAX_UPLOAD_SIZE:
                max_size_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
                raise ValidationError(_f('Размер файла не должен превышать {max_size_mb} МБ'))

            # Проверка расширения файла
            file_extension = document_file.name.split('.')[-1].lower()
            allowed_extensions = ['pdf', 'jpg', 'jpeg']

            if file_extension not in allowed_extensions:
                raise ValidationError(_('Допустимые форматы файлов: PDF, JPG'))

        return document_file

    def clean_additional_emails(self):
        """Проверка корректности списка дополнительных email адресов"""
        additional_emails = self.cleaned_data.get('additional_emails', '')

        if additional_emails:
            emails = [email.strip() for email in additional_emails.split(',')]

            for email in emails:
                try:
                    validate_email(email)
                except ValidationError:
                    raise ValidationError(_f('Email адрес "{email}" некорректен'))

        return additional_emails

    def save(self, commit=True):
        """Переопределение метода save для сохранения связанных напоминаний"""
        document = super().save(commit=commit)

        if commit:
            # Сохраняем стандартные периоды напоминаний
            selected_periods = self.cleaned_data.get('reminder_periods', [])
            if selected_periods:
                # Преобразуем в int, т.к. из формы значения приходят как строки
                selected_periods = [int(period) for period in selected_periods]

            # Добавляем пользовательский период, если задан
            custom_period = self.cleaned_data.get('custom_reminder_period')
            if custom_period:
                selected_periods.append(custom_period)

            # Получаем текущие периоды для документа
            existing_periods = document.reminders.values_list('days_before_expiry', flat=True)

            # Удаляем напоминания, которые были отключены
            for period in existing_periods:
                if period not in selected_periods:
                    document.reminders.filter(days_before_expiry=period).delete()

            # Добавляем новые периоды
            for period in selected_periods:
                if period not in existing_periods:
                    Reminder.objects.create(
                        document=document,
                        days_before_expiry=period
                    )

        return document

    class Meta:
        model = Document
        fields = [
            'title', 'received_date', 'expiry_date',
            'responsible_name', 'responsible_email', 'additional_emails',
            'document_file', 'comments'
        ]
        widgets = {
            'received_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }


class DocumentFilterForm(forms.Form):
    """Форма для фильтрации списка документов"""

    STATUS_CHOICES = [
        ('', _('Все статусы')),
        ('active', _('Действительны')),
        ('expiring_soon', _('Скоро истекают')),
        ('expired', _('Просрочены')),
    ]

    title = forms.CharField(
        required=False,
        label=_('Название документа'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Поиск по названию...'),
            'class': 'form-control'
        })
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        label=_('Статус')
    )

    responsible_name = forms.CharField(
        required=False,
        label=_('Ответственный'),
        widget=forms.TextInput(attrs={'placeholder': _('Имя ответственного...')})
    )

    expiry_date_from = forms.DateField(
        required=False,
        label=_('Срок действия с'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    expiry_date_to = forms.DateField(
        required=False,
        label=_('Срок действия по'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )