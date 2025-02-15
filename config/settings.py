from pathlib import Path
from decouple import config
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=i9ndbi2s(($l^3lh^0p74-8o+0bm^h9d#rxxcvs-!c6if!h9i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('SETTING_DEBUGGING', cast=bool)

ALLOWED_HOSTS = config("SETTING_ALLOWED_HOSTS").split(",")  # 쉼표로 구분하여 리스트로 변환

if DEBUG:
    CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8000", "http://localhost:8000"]
else:
    CSRF_TRUSTED_ORIGINS = ["https://www.pictory.site"]


# 로그 관련
LOGGING_DIR = BASE_DIR / 'logs'
if not os.path.exists(LOGGING_DIR):
    os.makedirs(LOGGING_DIR)  # logs 디렉토리 생성

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOGGING_DIR, "django_errors.log"),
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "ERROR",
    },
}

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'diaries',
    'users',
    'django.contrib.sites',                   
]

SITE_ID = 1 


AUTH_USER_MODEL = 'users.User'


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                'utils.context_processors.notification',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('SETTING_DB_NAME'),
        'USER': config('SETTING_DB_USER'),
        'PASSWORD': config('SETTING_DB_PW'),
        'HOST': config('SETTING_DB_HOST'),
        'PORT': config('SETTiNG_DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

LOGIN_URL = '/login/'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = False  # False 로 설정해야 DB에 변경 된 TIME_ZONE 이 반영 됨 


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/home/ubuntu/Pictory/staticfiles/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # 전역 정적 파일 디렉토리
]

# Media files (사용자가 추가하는 미디어들 저장위치)
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# 파일 업로드 최대 크기 조정
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]


MAX_UPLOAD_SIZE = 5242880
DATA_UPLOAD_MAX_MEMORY_SIZE = None
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# .env 변수들 LOAD
KAKAO_CLIENT_ID=config('KAKAO_CLIENT_ID')
KAKAO_REDIRECT_URI=config('KAKAO_REDIRECT_URI')
NAVER_CLIENT_ID = config("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = config("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = config("NAVER_CALLBACK_URI")
KAKAO_APPKEY_JS = config("KAKAO_APPKEY_JS")
