# Django settings for hackeragenda project.

import os

from collections import OrderedDict

PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])
SUBPROJECT_PATH = os.path.split(PROJECT_PATH)[0]

BASE_DIR = PROJECT_PATH  # to avoid stupid warning from django 1.6

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

ALLOWED_HOSTS = ['*']

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

PREDEFINED_FILTERS = OrderedDict()
PREDEFINED_FILTERS["default"] = {
    "source": [],
    "exclude_source": [
        "agile_belgium",
        "aws_user_group_belgium",
        "bescala",
        "belgian_angularjs",
        "belgian_nodejs_user_group",
        "belgian_puppet_user_group",
        "belgian_ruby_user_group",
        "bigdata_be",
        "budalab",
        "brussels_cassandra_users",
        "brussels_data_science_meetup",
        "brussels_wordpress",
        "docker_belgium",
        "ember_js_brussels",
        "imal",
        "laravel_brussels",
        "les_mardis_de_l_agile",
        "mongodb_belgium",
        "phpbenelux",
        "relab",
        "ruby_burgers",
        "timelab",
        "webrtc",
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
        "opengarage",
        "syn2cat",
        "urlab",
        "voidwarranties",
        "whitespace",
        "wolfplex"
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["*lab"] = {
    "source": [
        "budalab",
        "imal",
        "relab",
        "timelab",
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["art"] = {
    "source": [
        "belgian_blender_user_group",
        "blender_brussels",
        "constantvzw",
        "foam",
        "imal",
        "okno",
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["code"] = {
    "source": [
        "afpyro",
        "agile_belgium",
        "aws_user_group_belgium",
        "bescala",
        "belgian_angularjs",
        "belgian_puppet_user_group",
        "belgian_nodejs_user_group",
        "bigdata_be",
        "brussels_cassandra_users",
        "brussels_data_science_meetup",
        "brussels_wordpress",
        "docker_belgium",
        "ember_js_brussels",
        "laravel_brussels",
        "les_mardis_de_l_agile",
        "mongodb_belgium",
        "opentechschool",
        "phpbenelux",
        "ruby_burgers",
        "webrtc",
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        # Needed for the admin interface
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'hackeragenda.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'hackeragenda.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(SUBPROJECT_PATH, "templates"),
)

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (50.6407351, 4.66696),
    'DEFAULT_ZOOM': 7,
    'MIN_ZOOM': 2,
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'djangobower',
    'authentication',
    'administration',
    'events',
    'taggit',
    'gunicorn',
    'leaflet',
)

BOWER_INSTALLED_APPS = (
    'fullcalendar#1.6.4',
    'snapjs',
)

AGENDA = "be"

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
        'django_pdb',
        'django_extensions',
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

LOGIN_REDIRECT_URL = '/administration/'

try:
    from settings_local import *
except ImportError:
    pass
