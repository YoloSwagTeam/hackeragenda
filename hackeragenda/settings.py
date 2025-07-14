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

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite",
    }
}

# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = "Europe/Brussels"

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

USE_I18N = True

USE_L10N = True

USE_TZ = False

MEDIA_ROOT = ""
MEDIA_URL = "/medias/"

STATIC_ROOT = SUBPROJECT_PATH + "/static_deploy/static/"
STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(SUBPROJECT_PATH, "static"),)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

SECRET_KEY = "t)^bq6!v8!vj$+t+!4x1+uj100d73_8pt5d1(gh=py=lz7$^vm"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(SUBPROJECT_PATH, "templates"),
        ],
        # 'APP_DIRS': True,
        "OPTIONS": {
            "loaders": [
                "hamlpy.template.loaders.HamlPyFilesystemLoader",
                "hamlpy.template.loaders.HamlPyAppDirectoriesLoader",
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

PREDEFINED_FILTERS = OrderedDict()
PREDEFINED_FILTERS["default"] = {
    "source": [
        "afpyro",
        "agenda_du_libre_be",
        "belgian_blender_user_group",
        "belgium_python_meetup",
        "bhackspace",
        "blender_brussels",
        "brixel",
        "bxlug",
        "constantvzw",
        "F_LAT",
        "foam",
        "hsbxl",
        "incubhacker",
        "jeudi_du_libre_mons",
        "ko_lab",
        "makilab",
        "neutrinet",
        "npbbxl",
        "okfnbe",
        "okno",
        "opengarage",
        "opengarage_meetings",
        "openstreetmap_belgium",
        "opentechschool",
        "owaspbe",
        "realize",
        "source",
        "syn2cat",
        "urlab",
        "voidwarranties",
        "whitespace",
        "wolfplex",
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": ["meeting", "on_reservation"],
}

PREDEFINED_FILTERS["all"] = {
    "source": [],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["hackerspaces"] = {
    "source": [
        "brixel",
        "bhackspace",
        "hsbxl",
        "incubhacker",
        "opengarage",
        "syn2cat",
        "urlab",
        "voidwarranties",
        "whitespace",
        "wolfplex",
        "ko_lab",
    ],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["*lab"] = {
    "source": [],
    "exclude_source": [],
    "tag": ["fablab"],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["art"] = {
    "source": [],
    "exclude_source": [],
    "tag": ["art"],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["code"] = {
    "source": [],
    "exclude_source": [],
    "tag": ["code"],
    "exclude_tag": [],
}

if DEBUG:
    MIDDLEWARE += (
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        # Needed for the admin interface
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
    )

INTERNAL_IPS = ("127.0.0.1",)

ROOT_URLCONF = "hackeragenda.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "hackeragenda.wsgi.application"

LEAFLET_CONFIG = {
    "DEFAULT_CENTER": (50.6407351, 4.66696),
    "DEFAULT_ZOOM": 7,
    "MIN_ZOOM": 2,
}

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "authentication",
    "administration",
    "events",
    "taggit",
    "gunicorn",
    "leaflet",
)

AGENDA = "be"

if DEBUG:
    INSTALLED_APPS += (
        "debug_toolbar",
        "django_pdb",
        "django_extensions",
    )

FIXTURE_DIRS = ("fixtures",)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}

SOUTH_MIGRATION_MODULES = {
    "taggit": "taggit.south_migrations",
}

LOGIN_REDIRECT_URL = "/administration/"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

try:
    from hackeragenda.settings_local import *  # noqa
except ImportError:
    pass
