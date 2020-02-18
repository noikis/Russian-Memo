from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView

from .models import User, Student
from .forms import StudentSignUpForm, TeacherSignUpForm
from .decorators import student_required, teacher_required


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'account/student_signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        auth.login(self.request, user)
        return render(self.request, 'pages/index.html')


class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = 'account/teacher_signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'teacher'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        auth.login(self.request, user)
        return render(self.request, 'pages/index.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # authentification
        user = auth.authenticate(username=username, password=password)

        # if user is in the Database
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are registrated!')
            return redirect('account:dashboard')
        # user not Found
        else:
            messages.error(request, "Bad credentials.")
            return redirect('account:login')

    # accessing the login page
    else:
        return render(request, 'account/login.html')


def logout(request):
    auth.logout(request)
    # messages.success(request, "Вы вышли")
    return render(request, 'pages/index.html')


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')
