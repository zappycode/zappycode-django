import os
import environ

env = environ.Env()
environ.Env.read_env()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY', default='ThisIsAWeakSauceSecretKey')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.str('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # My Apps
    'courses',
    'sitewide',
    'challenge',
    'posts',
    'money',

    # 3rd Party
    'djcelery_email',
    'django_celery_results',

    # All Auth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zappycode.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'zappycode.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': env.str('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': env.str('DB_NAME', default=os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': env.str('DB_USER', default=''),
        'PASSWORD': env.str('DB_PASSWORD', default=''),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Authentication
AUTH_USER_MODEL = 'sitewide.ZappyUser'

AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    # 'allauth.account.auth_backends.AuthenticationBackend',

    # switched on custom backend, uncommented default.
    # source in sitewide/overrided_auth_backend.py
    'sitewide.overrided_auth_backend.NewRestrictionAuthenticationBackend',

)

# Required by allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
LOGIN_REDIRECT_URL = 'all_courses'
ACCOUNT_LOGOUT_REDIRECT_URL = 'home'
LOGIN_URL = 'account_login'

# Site Id that allauth makes us use
SITE_ID = 1

# Admin - For emailing errors
ADMINS = [(env.str('ADMIN_NAME', default='root'), env.str('ADMIN_EMAIL', default='root@localhost'))]

# Email

# To test sending an email
# from django.core.mail import send_mail
# send_mail('subject', 'body of the message', 'joe@zappycode.com', ['nwalter@gmail.com'])

EMAIL_HOST = env.str('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=0)
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'ZappyCode <nick@ZappyCode.com>'

# Celery Setup
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
CELERY_RESULT_BACKEND = 'django-db'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
