from django.urls import include, path
from django.contrib import admin
from django.conf import settings

from events.views import HomeView

admin.autodiscover()

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('authentication.urls')),
    path('administration/', include('administration.urls')),
    path('admin/', admin.site.urls),
    path('events/', include('events.urls')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
