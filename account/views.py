import hashlib
import hmac
import time

from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView
from django.views.decorators.csrf import csrf_exempt

from .models import User, Student
from .forms import StudentSignUpForm, TeacherSignUpForm
from .decorators import student_required, teacher_required


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'account/student_signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        kwargs['telegram_bot'] = getattr(settings, 'TELEGRAM_BOT_NAME', None)
        kwargs['telegram_auth_url'] = self.request.build_absolute_uri(
            str(reverse_lazy('account:telegram_auth'))
        )
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
            messages.success(request, 'You are loged in!')

            if user.is_student:
                return redirect('quiz:quiz_list_student')
            elif user.is_teacher:
                return redirect('quiz:quiz_list')
            else:
                return redirect('account:login')
        # user not Found
        else:
            messages.error(request, "Bad credentials.")
            return redirect('account:login')

    # accessing the login page
    else:
        return render(request, 'account/login.html')


def logout(request):
    auth.logout(request)
    messages.success(request, "Вы вышли")
    return redirect('account:login')


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html')


def _validate_telegram_payload(payload: dict):
    """
    Validate Telegram auth payload following https://core.telegram.org/widgets/login#checking-authorization.
    Returns (is_valid, data_or_error_message).
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        return False, 'Telegram login is not configured.'

    received_hash = payload.get('hash')
    if not received_hash:
        return False, 'Missing Telegram signature.'

    check_data = {k: v for k, v in payload.items() if k != 'hash'}
    check_string = '\n'.join(
        f'{key}={check_data[key]}' for key in sorted(check_data.keys())
    )
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(
        secret_key, check_string.encode(), hashlib.sha256
    ).hexdigest()
    if computed_hash != received_hash:
        return False, 'Telegram signature could not be verified.'

    try:
        auth_date = int(check_data.get('auth_date', 0))
    except (TypeError, ValueError):
        return False, 'Invalid auth date.'

    max_age = getattr(settings, 'TELEGRAM_LOGIN_MAX_AGE', 24 * 60 * 60)
    if auth_date and (time.time() - auth_date) > max_age:
        return False, 'Telegram login request expired.'

    return True, check_data


@csrf_exempt
def telegram_auth(request):
    """
    Create/login a student via Telegram Login Widget callback.
    """
    payload = request.GET.dict() if request.method == 'GET' else request.POST.dict()
    is_valid, data = _validate_telegram_payload(payload)
    if not is_valid:
        messages.error(request, data)
        return redirect('account:student_registration')

    telegram_id = data.get('id')
    if not telegram_id:
        messages.error(request, 'Telegram user id is required.')
        return redirect('account:student_registration')

    try:
        telegram_id_int = int(telegram_id)
    except (TypeError, ValueError):
        messages.error(request, 'Invalid Telegram user id.')
        return redirect('account:student_registration')

    student = (
        Student.objects.select_related('user')
        .filter(telegram_id=telegram_id_int)
        .first()
    )

    if student:
        user = student.user
        if not user.is_student:
            messages.error(request, 'Only students can log in with Telegram.')
            return redirect('account:login')
    else:
        username = data.get('username') or f'tg_{telegram_id_int}'
        base_username = username
        index = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}_{index}'
            index += 1

        user = User(
            username=username,
            first_name=data.get('first_name') or '',
            last_name=data.get('last_name') or '',
            is_student=True,
        )
        user.set_unusable_password()
        user.save()
        student = Student.objects.create(user=user, telegram_id=telegram_id_int)

    auth.login(request, user)
    messages.success(request, 'Добро пожаловать! Вы вошли через Telegram.')
    return redirect('quiz:quiz_list_student')
