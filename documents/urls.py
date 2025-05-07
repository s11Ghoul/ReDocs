from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'documents'

urlpatterns = [
    # Дашборд
    path('', views.dashboard_view, name='dashboard'),

    # Документы
    path(_('documents/'), views.DocumentListView.as_view(), name='document_list'),
    path(_('documents/add/'), views.DocumentCreateView.as_view(), name='document_create'),
    path(_('documents/<int:pk>/'), views.DocumentDetailView.as_view(), name='document_detail'),
    path(_('documents/<int:pk>/edit/'), views.DocumentUpdateView.as_view(), name='document_update'),
    path(_('documents/<int:pk>/delete/'), views.DocumentDeleteView.as_view(), name='document_delete'),

    # Логи
    path(_('logs/'), views.LogsListView.as_view(), name='logs_list'),
]