from django.shortcuts import render, redirect
from django.contrib import messages, auth

from .models import User


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # authentification
        user = auth.authenticate(username=username, password=password)

        # if user is in the Database
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Вы зарегистрированны!')
            return redirect('index')
        # user not Found
        else:
            messages.error(request, "'Введенные данны не совпадают")
            return redirect('login')

    # accessing the login page
    else:
        return render(request, 'users/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, "Вы вышли")
        return redirect('index')


def register_student(request):
    # Get form values
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            # if user already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Этот пользователь уже существует.")
                return redirect('register_student')

            else:
                # if email already used
                if User.objects.filter(email=email).exists():
                    messages.error(request, "Эту почту уже использувают.")
                    return redirect('register_student')
                # registration successfull!
                else:
                    # create user
                    user = User.objects.create_user(
                        username=username, password=password, email=email, first_name=first_name, last_name=last_name, is_student=True, is_teacher=False)
                    user.save()
                    # Login after registration
                    auth.login(request, user)
                    messages.success(request, "You are now logged in")

                    return redirect('index')

        else:
            # if passwords do not matchs
            messages.error(request, "Passwords do not match")
            return redirect('register_student')
    else:
        return render(request, 'users/register.html')
