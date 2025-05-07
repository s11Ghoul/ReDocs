from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Document, Reminder, EmailLog, HealthCheck
from .forms import DocumentForm, DocumentFilterForm


class StaffRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является персоналом (staff)"""

    def test_func(self):
        return self.request.user.is_staff


class DocumentListView(LoginRequiredMixin, ListView):
    """Представление для списка документов"""
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 10

    def get_queryset(self):
        """Получение отфильтрованного списка документов"""
        queryset = Document.objects.all()

        # Получаем параметры фильтрации из формы
        form = DocumentFilterForm(self.request.GET)

        if form.is_valid():
            # Фильтр по названию
            title = form.cleaned_data.get('title')
            if title:
                queryset = queryset.filter(title__icontains=title)

            # Фильтр по статусу
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)

            # Фильтр по ответственному
            responsible_name = form.cleaned_data.get('responsible_name')
            if responsible_name:
                queryset = queryset.filter(responsible_name__icontains=responsible_name)

            # Фильтр по дате окончания
            expiry_date_from = form.cleaned_data.get('expiry_date_from')
            if expiry_date_from:
                queryset = queryset.filter(expiry_date__gte=expiry_date_from)

            expiry_date_to = form.cleaned_data.get('expiry_date_to')
            if expiry_date_to:
                queryset = queryset.filter(expiry_date__lte=expiry_date_to)

        # Сортировка по дате окончания (ближайшие сверху)
        return queryset.order_by('expiry_date')

    def get_context_data(self, **kwargs):
        """Дополнительные данные для шаблона"""
        context = super().get_context_data(**kwargs)

        # Добавляем форму фильтрации
        context['filter_form'] = DocumentFilterForm(self.request.GET)

        # Добавляем статистику
        today = timezone.now().date()
        context['total_documents'] = Document.objects.count()
        context['active_documents'] = Document.objects.filter(status='active').count()
        context['expiring_soon_documents'] = Document.objects.filter(status='expiring_soon').count()
        context['expired_documents'] = Document.objects.filter(status='expired').count()

        return context


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """Представление для просмотра детальной информации о документе"""
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        """Дополнительные данные для шаблона"""
        context = super().get_context_data(**kwargs)

        # Получаем напоминания для документа
        context['reminders'] = self.object.reminders.all().order_by('-days_before_expiry')

        # Получаем историю отправки напоминаний
        context['email_logs'] = self.object.email_logs.all().order_by('-sent_at')[:10]

        return context


class DocumentCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания нового документа"""
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'
    success_url = reverse_lazy('documents:document_list')

    def form_valid(self, form):
        """Обработка валидной формы"""
        messages.success(self.request, _('Документ успешно создан.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Дополнительные данные для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = _('Создание нового документа')
        return context


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    """Представление для редактирования документа"""
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'

    def get_success_url(self):
        """URL для перенаправления после успешного обновления"""
        return reverse_lazy('documents:document_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        """Обработка валидной формы"""
        messages.success(self.request, _('Документ успешно обновлен.'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Дополнительные данные для шаблона"""
        context = super().get_context_data(**kwargs)
        context['title'] = _('Редактирование документа')
        return context


class DocumentDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Представление для удаления документа"""
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('documents:document_list')

    def delete(self, request, *args, **kwargs):
        """Обработка удаления документа"""
        messages.success(request, _('Документ успешно удален.'))
        return super().delete(request, *args, **kwargs)


class LogsListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Представление для просмотра логов отправки напоминаний"""
    model = EmailLog
    template_name = 'documents/logs_list.html'
    context_object_name = 'logs'
    paginate_by = 20

    def get_queryset(self):
        """Получение отфильтрованного списка логов"""
        return EmailLog.objects.all().order_by('-sent_at')

    def get_context_data(self, **kwargs):
        """Дополнительные данные для шаблона"""
        context = super().get_context_data(**kwargs)

        # Добавляем статистику логов
        context['total_logs'] = EmailLog.objects.count()
        context['successful_logs'] = EmailLog.objects.filter(status='sent').count()
        context['failed_logs'] = EmailLog.objects.filter(status='failed').count()

        # Добавляем логи проверок работоспособности
        context['health_checks'] = HealthCheck.objects.all().order_by('-check_date')[:10]

        return context


@login_required
def dashboard_view(request):
    """Представление для дашборда"""
    # Получаем статистику по документам
    today = timezone.now().date()

    context = {
        'total_documents': Document.objects.count(),
        'active_documents': Document.objects.filter(status='active').count(),
        'expiring_soon_documents': Document.objects.filter(status='expiring_soon').count(),
        'expired_documents': Document.objects.filter(status='expired').count(),

        # Документы, истекающие в ближайшие 30 дней
        'upcoming_expirations': Document.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timezone.timedelta(days=30)
        ).order_by('expiry_date')[:10],

        # Недавно просроченные документы
        'recent_expirations': Document.objects.filter(
            expiry_date__lt=today,
            expiry_date__gte=today - timezone.timedelta(days=30)
        ).order_by('-expiry_date')[:10],

        # Недавние уведомления
        'recent_notifications': EmailLog.objects.all().order_by('-sent_at')[:10],
    }

    return render(request, 'documents/dashboard.html', context)