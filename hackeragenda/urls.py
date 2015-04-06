from django.conf.urls import patterns, include, url
from django.contrib import admin

from events.views import HomeView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^events/', include('events.urls')),
)
