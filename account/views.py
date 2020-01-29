from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import CreateView

from .forms import StudentSignUpForm
from .models import User


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'account/registration.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return render(self.request, 'pages/index.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # authentification
        user = authenticate(username=username, password=password)

        # if user is in the Database
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы зарегистрированны!')
            return redirect('dashboard')
        # user not Found
        else:
            messages.error(request, "'Введенные данны не совпадают")
            return redirect('login')

    # accessing the login page
    else:
        return render(request, 'account/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        # messages.success(request, "Вы вышли")
        return redirect('index')


def dashboard(request):
    return render(request, 'account/dashboard.html')
