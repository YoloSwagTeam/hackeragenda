# Django settings for hackeragenda project.

from settings import *

PREDEFINED_FILTERS = OrderedDict()
PREDEFINED_FILTERS["default"] = {
    "source": [],
    "exclude_source": [],
    "tag": [],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["eating"] = {
    "source": [],
    "exclude_source": [],
    "tag": ['eating'],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["cooking class"] = {
    "source": [],
    "exclude_source": [],
    "tag": ['cooking class'],
    "exclude_tag": [],
}

PREDEFINED_FILTERS["animal rights"] = {
    "source": [],
    "exclude_source": [],
    "tag": ['animal-rights'],
    "exclude_tag": [],
}

AGENDA="vg_be"

from settings_vg_be_local import *
