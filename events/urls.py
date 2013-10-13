from django.conf.urls import patterns, url, include
from events.api import EventResource
from .feeds import NextEventsFeed

event_resource = EventResource()

urlpatterns = patterns('events.views',
    url(r'^events.json$', 'get_events_in_json', name='events_json'),
    url(r'^events.rss$', NextEventsFeed(), name='events_rss'),
    url(r'^api/', include(event_resource.urls), name='events_api'),
)
