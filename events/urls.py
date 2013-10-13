from django.conf.urls import patterns, url

urlpatterns = patterns('events.views',
    url(r'^events.json$', 'get_events_in_json', name='events_json'),
)
