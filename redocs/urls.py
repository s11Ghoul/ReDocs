from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Аутентификация
    path(_('login/'), auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path(_('logout/'), auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path(_('password-change/'), auth_views.PasswordChangeView.as_view(template_name='auth/password_change.html'), name='password_change'),
    path(_('password-change/done/'), auth_views.PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'), name='password_change_done'),

    # Основное приложение
    path('', include('documents.urls')),

    # Переключение языка
    path('i18n/', include('django.conf.urls.i18n')),
]

# В режиме разработки добавляем статические URL для обслуживания медиа-файлов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)