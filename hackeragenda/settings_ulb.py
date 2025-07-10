# Django settings for hackeragenda project.

from settings import *

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "fr-fr"

PREDEFINED_FILTERS = OrderedDict()
PREDEFINED_FILTERS["default"] = {
    "source": [],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": ["meeting"],
}

PREDEFINED_FILTERS["tout"] = {
    "source": [],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

AGENDA = "ulb"
