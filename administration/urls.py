from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django_view_dispatch import dispatch

from . import views


urlpatterns = patterns('administration.views',
    url(r'^$', login_required(dispatch(get=views.dashboard)), name='administration_dashboard'),
)
