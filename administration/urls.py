from django.conf.urls import patterns, url
from django_view_dispatch import dispatch
from django.views.generic.edit import DeleteView, UpdateView
from django.core.urlresolvers import reverse_lazy

from events.models import Event

from . import views

from .utils import user_can_add_events


urlpatterns = patterns('administration.views',
    url(r'^$', user_can_add_events(dispatch(get=views.dashboard, post=views.add_event)), name='administration_dashboard'),
    url(r'^event/(?P<pk>\d+)/update/$', user_can_add_events(UpdateView.as_view(model=Event, template_name="administration/event_form.haml", success_url=reverse_lazy('administration_dashboard'))), name='administration_event_update'),
    url(r'^event/(?P<pk>\d+)/delete/$', user_can_add_events(DeleteView.as_view(model=Event, template_name="administration/event_confirm_delete.haml", success_url=reverse_lazy('administration_dashboard'))), name='administration_event_delete'),
)
