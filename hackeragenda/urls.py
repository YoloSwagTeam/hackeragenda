from datetime import datetime

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import ListView

from events.models import Event
from events.views import EventListView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', EventListView.as_view(), name='home'),
    # url(r'^hackeragenda/', include('hackeragenda.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^events/', include('events.urls')),
)
