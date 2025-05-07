from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def custom_login(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', '/')
            return redirect(next_url)
        else:
            error = "Неверное имя пользователя или пароль"

    return render(request, 'auth/login_simple.html', {'error': error})

