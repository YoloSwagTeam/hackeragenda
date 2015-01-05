from django.conf.urls import patterns, url, include
from events.api import EventResource
from .feeds import NextEventsFeed
from .ics import get_ics_of_events
from .views import EventListView

event_resource = EventResource()

urlpatterns = patterns('events.views',
    url(r'^events.json$', 'get_events_in_json', name='events_json'),
    url(r'^events_for_map.json$', 'get_events_for_map_in_json', name='events_for_map_json'),
    url(r'^events.rss$', NextEventsFeed(), name='events_rss'),
    url(r'^events.ics$', get_ics_of_events, name='events_ics'),
    url(r'^events.html$', EventListView.as_view(), name='events_render'),
    url(r'^api/', include(event_resource.urls), name='events_api'),
)
