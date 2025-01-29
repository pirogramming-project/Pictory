from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

# 네이버 소셜 로그인 설정
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_CALLBACK_URL = os.getenv("NAVER_CALLBACK_URL")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=i9ndbi2s(($l^3lh^0p74-8o+0bm^h9d#rxxcvs-!c6if!h9i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


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
    'allauth',                               
    'allauth.account',                       
    'allauth.socialaccount',                
    'allauth.socialaccount.providers.naver', 
]

SITE_ID = 1 


# # 나 홀로 디버깅
# ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # username 필드 비활성화
# ACCOUNT_USERNAME_REQUIRED = False  # username 입력 비활성화

# ACCOUNT_AUTHENTICATION_METHOD = 'email'  # 이메일 또는 다른 필드를 인증 수단으로 사용
# ACCOUNT_EMAIL_REQUIRED = True  # 이메일 필드 필수
# ACCOUNT_EMAIL_VERIFICATION = 'optional'  # 이메일 검증 옵션 (필요에 따라 변경 가능)

# #요까지

SOCIALACCOUNT_PROVIDERS = {
    'naver': {
        'APP': {
            'client_id': NAVER_CLIENT_ID,
            'secret': NAVER_CLIENT_SECRET,
            'key': ''
        },
        'SCOPE': ['email', 'name'],
        'PROFILE_FIELDS': ['email', 'nickname'],
    }
}

LOGIN_REDIRECT_URL = '/'  # 로그인 성공 후 이동할 URL
LOGOUT_REDIRECT_URL = '/'  # 로그아웃 후 이동할 URL
ACCOUNT_LOGOUT_ON_GET = True  # GET 요청으로 로그아웃 허용

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  
    'allauth.account.auth_backends.AuthenticationBackend',  
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # 전역 정적 파일 디렉토리
]

# Media files (사용자가 추가하는 미디어들 저장위치)
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
