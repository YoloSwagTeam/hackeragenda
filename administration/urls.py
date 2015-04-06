from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import CreateEvent

urlpatterns = patterns('administration.views',
    url(r'^$', login_required(CreateEvent.as_view()), name='administration_dashboard'),
)
