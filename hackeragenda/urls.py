from datetime import datetime

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import ListView

from events.models import Event

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(queryset=Event.objects.filter(start__gte=datetime.now).order_by("start"), template_name="home.html"), name='home'),
    # url(r'^hackeragenda/', include('hackeragenda.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^events/', include('events.urls')),
)
