import sys
import os
from pathlib import Path
import json


BASE_PATH = Path(__file__).absolute().parent.parent


try:
    config_path = os.environ['VCMIS_ENV_FILE']
except KeyError:
    config_path = str(BASE_PATH / '.env.json')

try:
    with open(config_path) as f:
        config = json.load(f)
except Exception as e:
    import traceback
    print('''
Could not find or parse the VCMIS environment file: {}.

You must either have a .env.json file at the root of the project,
or set the VCMIS_ENV_FILE environment variable to a valid JSON
file containing the environment configuration.

In development, do the following to get started:
    ln -sr conf/envs/dev.json .env.json

The full error follows:

{}'''.format(e, traceback.format_exc()), file=sys.stderr, end='')
    sys.exit(1)


WSGI_APPLICATION = 'conf.wsgi.application'
ROOT_URLCONF = 'conf.urls'
DEBUG = config['debug']
SECRET_KEY = config['secret_key']
ALLOWED_HOSTS = config['allowed_hosts']
LANGUAGE_CODE = 'he'
LOCALE_PATHS = (
    str(BASE_PATH / 'locale'),
)
TIME_ZONE = 'Asia/Jerusalem'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/'
STATIC_ROOT = config['static_root']
SESSION_COOKIE_SECURE = config['https']
CSRF_COOKIE_SECURE = config['https']
ADMINS = config['admins']
AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_filters',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'corsheaders',
    'import_export',

    'users.apps.UsersConfig',
    'geography.apps.GeographyConfig',
    'recipients.apps.RecipientsConfig',
    'adoptions.apps.AdoptionsConfig',
    'logistics.apps.LogisticsConfig',
    'activities.apps.ActivitiesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config['db_name'],
        'USER': config['db_user'],
        'PASSWORD': config['db_password'],
        'HOST': config['db_host'],
        'PORT': config['db_port'],
        'CONN_MAX_AGE': 600,
    },
}

CACHES = {
    'default': {
        'BACKEND': config['cache_backend'],
        'LOCATION': config['cache_location'],
    },
}

STATICFILES_DIRS = [
    str(BASE_PATH.parent / 'client' / 'dist' / 'browser'),
]
STATICFILES_STORAGE = config['staticfiles_storage']

# "From" address for 500 emails.
SERVER_EMAIL = "VCMIS Errors <root@localhost>"
# "From" address for regular emails.
DEFAULT_FROM_EMAIL = config['from_email']
EMAIL_BACKEND = config['email_backend']
EMAIL_HOST = config['email_host']
EMAIL_PORT = config['email_port']
EMAIL_USE_TLS = config['email_use_tls']
EMAIL_HOST_USER = config['email_user']
EMAIL_HOST_PASSWORD = config['email_password']
EMAIL_TIMEOUT = 10

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default_logfmt': {
            'format': 'logger=%(name)s location=%(module)s.%(funcName)s:%(lineno)s  %(message)s',
        },
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[%(server_time)s] %(message)s',
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
            'formatter': 'default_logfmt',
        } if config['log_to_syslog'] else {
            'class': 'logging.StreamHandler',
            'formatter': 'default_logfmt',
        },
        'mail_admins': {
            'class': 'django.utils.log.AdminEmailHandler',
            'level': 'WARNING',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
    },
    'root': {
        'handlers': ['default', 'mail_admins'],
        'level': 'INFO',
    },
    'loggers': {
        'vcmis': {
            'propagate': True,
        },
        'django': {
            'level': 'ERROR',
            'propagate': True,
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        # Uncomment to log all SQL statements (for debugging/optimizing).
        # 'django.db.backends': {
        #     'level': 'DEBUG',
        # },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',

    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'URL_FORMAT_OVERRIDE': None,
    'FORMAT_SUFFIX_KWARG': None,
}

DJOSER = {
    'SEND_ACTIVATION_EMAIL': True,
    'ACTIVATION_URL': 'users/activate/{uid}/{token}',
    'PASSWORD_RESET_CONFIRM_URL': 'users/reset-password/{uid}/{token}',
}

CORS_ORIGIN_ALLOW_ALL = True


IMPORT_EXPORT_USE_TRANSACTIONS = True
