from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import HttpResponse
@csrf_exempt
def custom_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Используем конкретный URL вместо пустой строки
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            else:
                # Или перенаправляем на специфический URL по умолчанию
                return redirect('documents:dashboard')  # Убедитесь, что это имя существует
        else:
            error = "Неверное имя пользователя или пароль"

    return render(request, 'auth/login_simple.html', {'error': error})

