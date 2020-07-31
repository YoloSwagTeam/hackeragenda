from django.urls import path, include
from django.http import HttpResponse

from events.api import EventResource
from .feeds import NextEventsFeed
from .ics import get_ics_of_events
from .views import (
    EventListView,
    EventMonthArchiveView,
    EventWeekArchiveView,
    get_events_in_json,
    get_events_for_map_in_json,
)

event_resource = EventResource()

urlpatterns = [
    path("events.json", get_events_in_json, name="events_json"),
    path("events_for_map.json", get_events_for_map_in_json, name="events_for_map_json"),
    path("events.rss", NextEventsFeed(), name="events_rss"),
    path("events.ics", get_ics_of_events, name="events_ics"),
    path("events.html", EventListView.as_view(), name="events_render"),
    path(
        "month/<int:year>/<int:month>/",
        EventMonthArchiveView.as_view(allow_future=True),
        name="events_month",
    ),
    path(
        "week/<int:year>/<int:week>/",
        EventWeekArchiveView.as_view(allow_future=True),
        name="events_week",
    ),
    path(
        "location_cache.yaml",
        lambda _: HttpResponse(open("events/fixtures/location_cache.yaml", "r").read()),
        name="location_cache",
    ),
    path("api/", include(event_resource.urls), name="events_api"),
]
