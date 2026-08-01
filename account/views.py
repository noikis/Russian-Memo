import hashlib
import hmac
import base64
import secrets
import time
import json
import urllib.parse
import urllib.request
import urllib.error
from init_data_py import InitData 
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.http import url_has_allowed_host_and_scheme

from .models import ExternalIdentity, Role, User
from .forms import StudentSignUpForm, TeacherSignUpForm
from .decorators import student_required, teacher_required

TELEGRAM_PROVIDER = "telegram"
VK_PROVIDER = "vk"


def _vk_is_configured():
    return bool(getattr(settings, 'VK_APP_ID', None) and getattr(settings, 'VK_APP_SECRET', None))


def _vk_mini_app_is_configured():
    return _vk_is_configured()


def _with_next_param(base_url: str, next_url: str):
    if not next_url:
        return base_url
    return f"{base_url}?{urllib.parse.urlencode({'next': next_url})}"


def _vk_redirect_base():
    host = getattr(settings, 'HOST', 'localhost')
    if host.startswith('localhost') or host.startswith('127.0.0.1'):
        scheme = 'http'
    else:
        scheme = 'https'
    return f"{scheme}://{host}"


def _vk_redirect_uri():
    return f"{_vk_redirect_base()}{reverse_lazy('account:vk_oauth_callback')}"


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
        next_url = self.request.GET.get('next')
        vk_start_url = str(reverse_lazy('account:vk_oauth_start'))
        kwargs['vk_login_url'] = _with_next_param(vk_start_url, next_url)
        kwargs['vk_login_enabled'] = _vk_is_configured()
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
            messages.success(request, 'Вы вошли в систему.')

            if user.is_student:
                return redirect('quiz:quiz_list_student')
            elif user.is_teacher:
                return redirect('quiz:quiz_list')
            else:
                return redirect('account:login')
        # user not Found
        else:
            messages.error(request, "Неверные учетные данные.")
            return redirect('account:login')

    # accessing the login page
    else:
        next_url = request.GET.get('next')
        vk_start_url = str(reverse_lazy('account:vk_oauth_start'))
        context = {
            'next': next_url,
            'vk_login_url': _with_next_param(vk_start_url, next_url),
            'vk_login_enabled': _vk_is_configured(),
        }
        return render(request, 'account/login.html', context)


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
        return False, 'Вход через Telegram не настроен.'

    received_hash = payload.get('hash')
    if not received_hash:
        return False, 'Отсутствует подпись Telegram.'

    check_data = {k: v for k, v in payload.items() if k != 'hash'}
    check_string = '\n'.join(
        f'{key}={check_data[key]}' for key in sorted(check_data.keys())
    )
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(
        secret_key, check_string.encode(), hashlib.sha256
    ).hexdigest()
    if computed_hash != received_hash:
        return False, 'Подпись Telegram не прошла проверку.'

    try:
        auth_date = int(check_data.get('auth_date', 0))
    except (TypeError, ValueError):
        return False, 'Некорректная дата авторизации.'

    max_age = getattr(settings, 'TELEGRAM_LOGIN_MAX_AGE', 24 * 60 * 60)
    if auth_date and (time.time() - auth_date) > max_age:
        return False, 'Срок действия запроса на вход через Telegram истек.'

    return True, check_data


def _validate_webapp_init_data(init_data_raw: str):
    """
    Validate Telegram WebApp initData (mini app) following
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app.
    Returns (is_valid, data_dict_or_error).
    """
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    if not bot_token:
        return False, 'Вход через Telegram не настроен.'
    if not init_data_raw:
        return False, 'Отсутствуют initData.'

    max_age = getattr(settings, 'TELEGRAM_LOGIN_MAX_AGE', 24 * 60 * 60)

    if not InitData:
        return False, 'Для проверки Telegram initData требуется init-data-py.'

    try:
        init_data = InitData.parse(init_data_raw)

        is_valid = init_data.validate(
            bot_token=bot_token,
            lifetime=max_age,
        )
        if not is_valid:
            return False, 'ÐŸÐ¾Ð´Ð¿Ð¸ÑÑŒ Telegram Ð½Ðµ Ð¿Ñ€Ð¾ÑˆÐ»Ð° Ð¿Ñ€Ð¾Ð²ÐµÑ€ÐºÑƒ.'

        user = init_data.user  # parsed user object (if valid)
        return True, user
    except Exception as exc:
        return False, f'Подпись Telegram не прошла проверку ({exc}).'


def _get_telegram_field(user_data, key, default=None):
    if isinstance(user_data, dict):
        return user_data.get(key, default)
    return getattr(user_data, key, default)


def _parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _vk_http_get(url: str, params: dict):
    try:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        with urllib.request.urlopen(full_url, timeout=10) as resp:
            body = resp.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode('utf-8')
        except Exception:
            body = str(exc)
        return None, f"Ошибка VK OAuth ({exc.code}): {body}"
    except Exception as exc:
        return None, f"Ошибка VK OAuth: {exc}"

    try:
        return json.loads(body), None
    except json.JSONDecodeError:
        return None, "Некорректный ответ VK OAuth."


def _normalize_vk_profile(profile: dict):
    if not profile:
        return {}
    return {
        'username': profile.get('screen_name'),
        'first_name': profile.get('first_name'),
        'last_name': profile.get('last_name'),
        'photo_url': profile.get('photo_200'),
    }


def _validate_vk_mini_app_launch_params(launch_params_raw: str):
    if not _vk_mini_app_is_configured():
        return False, 'VK Mini App auth is not configured.'
    if not launch_params_raw:
        return False, 'Missing VK Mini App launch parameters.'

    parsed = urllib.parse.parse_qs(
        launch_params_raw.lstrip('?'),
        keep_blank_values=True,
    )
    payload = {key: values[0] for key, values in parsed.items()}
    received_sign = payload.get('sign')
    if not received_sign:
        return False, 'Missing VK Mini App signature.'

    vk_params = {
        key: value
        for key, value in payload.items()
        if key.startswith('vk_')
    }
    sign_payload = urllib.parse.urlencode(dict(sorted(vk_params.items())))
    computed_sign = base64.urlsafe_b64encode(
        hmac.new(
            settings.VK_APP_SECRET.encode(),
            sign_payload.encode(),
            hashlib.sha256,
        ).digest()
    ).decode().rstrip('=')

    if not hmac.compare_digest(computed_sign, received_sign):
        return False, 'Invalid VK Mini App signature.'

    if str(payload.get('vk_app_id')) != str(settings.VK_APP_ID):
        return False, 'Invalid VK Mini App id.'

    vk_user_id = _parse_int(payload.get('vk_user_id'))
    if vk_user_id is None:
        return False, 'Missing VK Mini App user id.'

    vk_ts = _parse_int(payload.get('vk_ts'))
    max_age = int(getattr(settings, 'VK_MINI_APP_AUTH_MAX_AGE', 60 * 60))
    if vk_ts and max_age and (time.time() - vk_ts) > max_age:
        return False, 'VK Mini App launch parameters expired.'

    return True, payload


def _make_unique_username(base: str):
    if not User.objects.filter(username=base).exists():
        return base
    while True:
        candidate = f"{base}_{secrets.token_hex(3)}"
        if not User.objects.filter(username=candidate).exists():
            return candidate


def _get_or_create_student_from_vk(user_id, profile):
    vk_id = _parse_int(user_id)
    if vk_id is None:
        return None, 'Некорректный идентификатор VK.'

    identity = (
        ExternalIdentity.objects.select_related('user')
        .filter(provider=VK_PROVIDER, provider_user_id=vk_id)
        .first()
    )
    normalized = _normalize_vk_profile(profile)
    if identity:
        user = identity.user
        if not user.is_student():
            return None, 'Вход через VK доступен только ученикам.'
        _update_external_identity(identity, normalized)
        return user, None

    with transaction.atomic():
        username = normalized.get('username') or f'vk_user_{vk_id}'
        username = _make_unique_username(username)

        user = User(
            username=username,
            first_name=normalized.get('first_name') or '',
            last_name=normalized.get('last_name') or '',
        )
        user.set_unusable_password()
        user.save()

        role, _ = Role.objects.get_or_create(name="student")
        user.roles.add(role)

        ExternalIdentity.objects.create(
            user=user,
            provider=VK_PROVIDER,
            provider_user_id=vk_id,
            username=normalized.get('username'),
            first_name=normalized.get('first_name'),
            last_name=normalized.get('last_name'),
            photo_url=normalized.get('photo_url'),
            auth_date=None,
            last_login_at=timezone.now(),
        )

    return user, None


def _update_external_identity(identity, user_data):
    update_fields = []

    username = _get_telegram_field(user_data, 'username')
    if username is not None:
        identity.username = username
        update_fields.append('username')

    first_name = _get_telegram_field(user_data, 'first_name')
    if first_name is not None:
        identity.first_name = first_name
        update_fields.append('first_name')

    last_name = _get_telegram_field(user_data, 'last_name')
    if last_name is not None:
        identity.last_name = last_name
        update_fields.append('last_name')

    photo_url = _get_telegram_field(user_data, 'photo_url')
    if photo_url is not None:
        identity.photo_url = photo_url
        update_fields.append('photo_url')

    auth_date = _parse_int(_get_telegram_field(user_data, 'auth_date'))
    if auth_date is not None:
        identity.auth_date = auth_date
        update_fields.append('auth_date')

    identity.last_login_at = timezone.now()
    update_fields.append('last_login_at')

    identity.save(update_fields=update_fields)


def _get_or_create_student_from_telegram(user_data):
    telegram_id = _parse_int(_get_telegram_field(user_data, 'id'))
    if telegram_id is None:
        return None, 'Некорректный идентификатор Telegram.'

    identity = (
        ExternalIdentity.objects.select_related('user')
        .filter(provider=TELEGRAM_PROVIDER, provider_user_id=telegram_id)
        .first()
    )
    if identity:
        user = identity.user
        if not user.is_student():
            return None, 'Вход через Telegram доступен только ученикам.'
        _update_external_identity(identity, user_data)
        return user, None

    with transaction.atomic():
        username = (
            _get_telegram_field(user_data, 'username')
            or f'tg_user_{telegram_id}'
        )
        username = _make_unique_username(username)

        user = User(
            username=username,
            first_name=_get_telegram_field(user_data, 'first_name') or '',
            last_name=_get_telegram_field(user_data, 'last_name') or '',
        )
        user.set_unusable_password()
        user.save()

        role, _ = Role.objects.get_or_create(name="student")
        user.roles.add(role)

        identity = ExternalIdentity.objects.create(
            user=user,
            provider=TELEGRAM_PROVIDER,
            provider_user_id=telegram_id,
            username=_get_telegram_field(user_data, 'username'),
            first_name=_get_telegram_field(user_data, 'first_name'),
            last_name=_get_telegram_field(user_data, 'last_name'),
            photo_url=_get_telegram_field(user_data, 'photo_url'),
            auth_date=_parse_int(_get_telegram_field(user_data, 'auth_date')),
            last_login_at=timezone.now(),
        )

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


@method_decorator(csrf_exempt, name='dispatch')
class VKMiniAppAuthView(View):
    """
    Auto-login for VK Mini App using signed launch parameters.
    """

    def post(self, request, *args, **kwargs):
        launch_params_raw = request.POST.get('launch_params')
        is_valid, data = _validate_vk_mini_app_launch_params(launch_params_raw)
        if not is_valid:
            return JsonResponse({'ok': False, 'error': data}, status=400)

        profile = None
        profile_raw = request.POST.get('profile')
        if profile_raw:
            try:
                profile = json.loads(profile_raw)
            except json.JSONDecodeError:
                profile = None

        user, error = _get_or_create_student_from_vk(data.get('vk_user_id'), profile)
        if error:
            return JsonResponse({'ok': False, 'error': error}, status=400)

        auth.login(request, user)
        redirect_url = str(reverse_lazy('quiz:quiz_list_student'))
        return JsonResponse({'ok': True, 'redirect': redirect_url})


class VKMiniAppAuthPageView(TemplateView):
    """
    Renders the mini-app auth bootstrap page that posts VK launch params.
    """
    template_name = 'account/vk_mini_app_auth.html'


def vk_oauth_start(request):
    if not _vk_is_configured():
        messages.error(request, 'Вход через VK не настроен.')
        return redirect('account:login')

    state = secrets.token_urlsafe(24)
    request.session['vk_oauth_state'] = state

    next_url = request.GET.get('next')
    if next_url:
        request.session['vk_oauth_next'] = next_url
    else:
        request.session.pop('vk_oauth_next', None)

    params = {
        'client_id': settings.VK_APP_ID,
        'redirect_uri': _vk_redirect_uri(),
        'response_type': 'code',
        'state': state,
        'v': settings.VK_OAUTH_VERSION,
    }
    return redirect(f"https://oauth.vk.com/authorize?{urllib.parse.urlencode(params)}")


def vk_oauth_callback(request):
    if not _vk_is_configured():
        messages.error(request, 'Вход через VK не настроен.')
        return redirect('account:login')

    expected_state = request.session.pop('vk_oauth_state', None)
    state = request.GET.get('state')
    if not expected_state or not state or state != expected_state:
        messages.error(request, 'Неверное состояние авторизации VK.')
        return redirect('account:login')

    if request.GET.get('error'):
        error_desc = request.GET.get('error_description') or 'Неизвестная ошибка VK.'
        messages.error(request, f'Ошибка VK: {error_desc}')
        return redirect('account:login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Отсутствует код авторизации VK.')
        return redirect('account:login')

    token_payload, token_error = _vk_http_get(
        'https://oauth.vk.com/access_token',
        {
            'client_id': settings.VK_APP_ID,
            'client_secret': settings.VK_APP_SECRET,
            'redirect_uri': _vk_redirect_uri(),
            'code': code,
        },
    )
    if token_error or not token_payload:
        messages.error(request, token_error or 'Не удалось получить токен VK.')
        return redirect('account:login')

    if token_payload.get('error'):
        messages.error(request, f"Ошибка VK: {token_payload.get('error_description') or token_payload.get('error')}")
        return redirect('account:login')

    access_token = token_payload.get('access_token')
    user_id = token_payload.get('user_id')
    if not access_token or not user_id:
        messages.error(request, 'Некорректный ответ VK OAuth.')
        return redirect('account:login')

    profile = None
    profile_payload, profile_error = _vk_http_get(
        'https://api.vk.com/method/users.get',
        {
            'user_ids': user_id,
            'fields': 'screen_name,photo_200',
            'access_token': access_token,
            'v': settings.VK_OAUTH_VERSION,
        },
    )
    if not profile_error and profile_payload and profile_payload.get('response'):
        profile = profile_payload['response'][0]

    user, error = _get_or_create_student_from_vk(user_id, profile)
    if error:
        messages.error(request, error)
        return redirect('account:login')

    auth.login(request, user)
    messages.success(request, 'Добро пожаловать! Вы вошли через VK.')

    next_url = request.session.pop('vk_oauth_next', None)
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host(), getattr(settings, 'HOST', '')},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect('quiz:quiz_list_student')
