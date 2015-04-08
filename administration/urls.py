from django.conf.urls import patterns, url
from django_view_dispatch import dispatch

from . import views

from .utils import user_can_add_events


urlpatterns = patterns('administration.views',
    url(r'^$', user_can_add_events(dispatch(get=views.dashboard, post=views.add_event)), name='administration_dashboard'),
)
