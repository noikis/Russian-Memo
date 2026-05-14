import os
from pathlib import Path

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env if present (simple parser to avoid extra deps)
ENV_PATH = Path(BASE_DIR) / '.env'
if ENV_PATH.is_file():
    with ENV_PATH.open() as env_file:
        for line in env_file:
            if not line or line.lstrip().startswith('#') or '=' not in line:
                continue
            key, _, value = line.strip().partition('=')
            if key and value and key not in os.environ:
                os.environ[key] = value


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '(^zh-0=n*kad5k@=5_v*@x!-^xm0@4t2bae==gik3bt(z#!#h7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = [os.environ.get('HOST', 'localhost'), '127.0.0.1', 'localhost']


# Application definition

INSTALLED_APPS = [
    'crispy_forms',
    'crispy_forms_materialize',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django.contrib.staticfiles',
    'bot',
    'memorisation',
    'quiz',
    'words',
    'account',
]

MIDDLEWARE = [
   # 'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'russian_memo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'russian_memo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Django Auth Settings
ACCOUNT_EMAIL_REQUIRED = False

AUTH_USER_MODEL = 'account.User'

# LOGIN_URL = 'account/login/'

LOGOUT_URL = 'logout'

LOGIN_REDIRECT_URL = 'home'

LOGOUT_REDIRECT_URL = 'home'


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "ru"
LANGUAGES = [("ru", "Russian")]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'russian_memo/assets')
]


# MEDIA folder
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

# Default layout to use with "crispy_forms"
CRISPY_TEMPLATE_PACK = 'materialize_css_forms'

MATERIAL_ADMIN_SITE = {
    'HEADER':  'Russian Memo',  # Admin site header
    'TITLE': ('Russian Memo'),  # Admin site title
    'SHOW_THEMES':  True,  # Show default admin themes button
    'TRAY_REVERSE': True,  # Hide object-tools and additional-submit-line by default
    'SHOW_COUNTS': True,  # Show instances counts for each model
    'APP_ICONS': {  # Set icons for applications(lowercase), including 3rd party apps, {'application_name': 'material_icon_name', ...}
        'account': 'people',
        'words': 'language',
        'quiz': 'list_alt',
        'memorisation': 'games',
    },
    'MODEL_ICONS': {
        # Set icons for models(lowercase), including 3rd party models, {'model_name': 'material_icon_name',
        'user': 'person',
        'role': 'verified_user',
        'userrole': 'groups',
        'externalidentity': 'fingerprint',
        'deck': 'bookmarks',
        'card': 'bookmark',
        'question': 'not_listed_location',
        'answer': 'format_list_numbered',
        'quiz': 'list_alt',
        'quizattempt': 'done_all',
        'selectedanswer': 'check_circle',
        'cardpractice': 'update',
        'cardreview': 'history',

    }
}

# If you expose the site via a public domain (e.g., ngrok), add it here.
CSRF_TRUSTED_ORIGINS = [
    os.environ.get('HOST')
]

# Telegram Login
TELEGRAM_BOT_NAME = os.environ.get('TELEGRAM_BOT_NAME')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
try:
    TELEGRAM_LOGIN_MAX_AGE = int(os.environ.get('TELEGRAM_LOGIN_MAX_AGE', 24 * 60 * 60))
except (TypeError, ValueError):
    TELEGRAM_LOGIN_MAX_AGE = 24 * 60 * 60

# VK OAuth
VK_APP_ID = os.environ.get('VK_APP_ID')
VK_APP_SECRET = os.environ.get('VK_APP_SECRET')
VK_OAUTH_VERSION = os.environ.get('VK_OAUTH_VERSION', '5.131')
