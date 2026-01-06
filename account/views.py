import hashlib
import hmac
import time
import json
from init_data_py import InitData 
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest

from .models import User, Student
from .forms import StudentSignUpForm, TeacherSignUpForm
from .decorators import student_required, teacher_required


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = 'account/student_signup.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'student'
        kwargs['bot'] = getattr(settings, 'TELEGRAM_BOT_NAME', None)
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


def _validate_webapp_init_data(init_data_raw: str):
    """
    Validate Telegram WebApp initData (mini app) following
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app.
    Returns (is_valid, data_dict_or_error).
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        return False, 'Telegram login is not configured.'
    if not init_data_raw:
        return False, 'Missing initData.'

    max_age = getattr(settings, 'TELEGRAM_LOGIN_MAX_AGE', 24 * 60 * 60)

    if not InitData:
        return False, 'init-data-py is required to verify Telegram initData.'

    try:
        init_data = InitData.parse(init_data_raw)

        is_valid = init_data.validate(
            bot_token=bot_token,
            lifetime=3600,   # seconds
        )

        user = init_data.user  # parsed user object (if valid)
        return True, user
    except Exception as exc:
        return False, f'Telegram signature could not be verified ({exc}).'


def _get_or_create_student_from_telegram(user_data):
    student = (
        Student.objects.select_related('user')
        .filter(telegram_id=user_data.id)
        .first()
    )
    if student:
        user = student.user
        if not user.is_student:
            return None, 'Only students can log in with Telegram.'
        return user, None


    user = User(
        username=user_data.username or f'tg_user_{user_data.id}',
        first_name=user_data.first_name or '',
        last_name=user_data.last_name or '',
        is_student=True,
    )
    user.set_unusable_password()
    user.save()
    Student.objects.create(user=user, telegram_id=telegram_id_int)
    return user, None


@method_decorator(csrf_exempt, name='dispatch')
class TelegramAuthView(View):
    """
    Create/login a student via Telegram Login Widget callback (GET/POST).
    """

    def get(self, request, *args, **kwargs):
        return self.handle(request)

    def post(self, request, *args, **kwargs):
        return self.handle(request)

    def handle(self, request):
        payload = request.GET.dict() if request.method == 'GET' else request.POST.dict()
        is_valid, data = _validate_telegram_payload(payload)
        if not is_valid:
            messages.error(request, data)
            return redirect('account:student_registration')

        user, error = _get_or_create_student_from_telegram(data)
        if error:
            messages.error(request, error)
            return redirect('account:student_registration')

        auth.login(request, user)
        messages.success(request, 'Добро пожаловать! Вы вошли через Telegram.')
        return redirect('quiz:quiz_list_student')


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebAppAuthView(View):
    """
    Auto-login for Telegram mini app using initData (POST).
    """

    def post(self, request, *args, **kwargs):
        init_data_raw = request.POST.get('init_data')
        is_valid, data = _validate_webapp_init_data(init_data_raw)
        if not is_valid:
            return JsonResponse({'ok': False, 'error': data}, status=400)

        user, error = _get_or_create_student_from_telegram(data)
        if error:
            return JsonResponse({'ok': False, 'error': error}, status=400)

        auth.login(request, user)
        redirect_url = str(reverse_lazy('quiz:quiz_list_student'))
        return JsonResponse({'ok': True, 'redirect': redirect_url})


class TelegramMiniAppAuthPageView(TemplateView):
    """
    Renders the mini-app auth bootstrap page that posts initData to the backend.
    """
    template_name = 'account/telegram_mini_app_auth.html'
