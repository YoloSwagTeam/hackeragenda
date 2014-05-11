# Django settings for hackeragenda project.

import os

from collections import OrderedDict

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])
SUBPROJECT_PATH = os.path.split(PROJECT_PATH)[0]

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

ALLOWED_HOSTS = ['*']

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Brussels'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = False

MEDIA_ROOT = ''
MEDIA_URL = '/medias/'

STATIC_ROOT = SUBPROJECT_PATH + '/static_deploy/static/'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(SUBPROJECT_PATH, "static"),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'djangobower.finders.BowerFinder',
)

SECRET_KEY = 't)^bq6!v8!vj$+t+!4x1+uj100d73_8pt5d1(gh=py=lz7$^vm'

BOWER_COMPONENTS_ROOT = SUBPROJECT_PATH + '/bower/'

TEMPLATE_LOADERS = (
    'hamlpy.template.loaders.HamlPyFilesystemLoader',
    'hamlpy.template.loaders.HamlPyAppDirectoriesLoader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

PREDEFINED_FILTERS = OrderedDict()
PREDEFINED_FILTERS["default"] = {
    "source": [],
    "exclude_source": [
        "agile_belgium",
        "bescala",
    ],
    "tag": [],
    "exclude_tag": ["meeting"],
}

PREDEFINED_FILTERS["all"] = {
    "source": [],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["hackerspaces"] = {
    "source": [
        "bhackspace",
        "hsbxl",
        "incubhacker",
        "urlab",
        "voidwarranties",
        "whitespace",
        "wolfplex"
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["code"] = {
    "source": [
        "afpyro",
        "agile_belgium",
        "bescala",
        "opentechschool"
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'hackeragenda.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'hackeragenda.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(SUBPROJECT_PATH, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'south',
    'djangobower',
    'events',
    'taggit',
)

BOWER_INSTALLED_APPS = (
    'fullcalendar',
    'snapjs',
)

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
        'django_pdb',
        'django_extensions',
    )

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

FIXTURE_DIRS = (
    'fixtures',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

SOUTH_MIGRATION_MODULES = {
    'taggit': 'taggit.south_migrations',
}


try:
    from settings_local import *
except ImportError:
    pass
