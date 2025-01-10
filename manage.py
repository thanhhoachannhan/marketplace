
import os, sys
from pathlib import Path

from django.core.management import execute_from_command_line
from django.utils.translation import gettext_lazy as _


BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = 'django'

DEBUG = True

ROOT_URLCONF = 'urls'

#-------------------------------------------------
# Media
#-------------------------------------------------
MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]

#-------------------------------------------------
# Timezone
#-------------------------------------------------
# USE_TZ = True
# USE_L10N = True
# TIME_ZONE = 'UTC'

#-------------------------------------------------
# Languages
#-------------------------------------------------
USE_I18N = True
LANGUAGE_CODE = 'en'
LOCALE_PATHS = [BASE_DIR / 'locale/',]
LANGUAGES = (
    ('en', _('English')),
    ('vi', _('Vietnamese')),
)
if not os.path.exists(BASE_DIR / 'locale'): os.mkdir('locale')
for lang in LANGUAGES:
    if not os.path.exists(BASE_DIR / 'locale' / lang[0]):
        os.mkdir(BASE_DIR / 'locale' / lang[0])
    if not os.path.exists(BASE_DIR / 'locale' / lang[0] / 'LC_MESSAGES'):
        os.mkdir(BASE_DIR / 'locale' / lang[0] / 'LC_MESSAGES')

#-------------------------------------------------
# Apps Settings
#-------------------------------------------------
INSTALLED_APPS = [
    'app.apps.AppConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

#-------------------------------------------------
# Middleware
#-------------------------------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Multiple languages
    'django.middleware.locale.LocaleMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Fix: Cannot query 'None(User)': Must be 'Group' instance.
    'app.middleware.BlockNormalUserMiddleware',
]

#-------------------------------------------------
# Templates
#-------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
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

#-------------------------------------------------
# Databases
#-------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

#-------------------------------------------------
# Authentication Settings
#-------------------------------------------------
AUTH_USER_MODEL = 'app.User'

# Process: Inactive Errors messagse when login
AUTHENTICATION_BACKENDS = ['app.backends.AuthenticationBackend']

#-------------------------------------------------
# Email
#-------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'emails'

#-------------------------------------------------
# Logging
#-------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'log.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
    },
}


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manage')
    execute_from_command_line(sys.argv)