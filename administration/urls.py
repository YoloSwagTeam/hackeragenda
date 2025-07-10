from django.urls import path, reverse_lazy
from django.views.generic.edit import DeleteView

from events.models import Event

from . import views

from .utils import user_can_add_events


urlpatterns = [
    path(
        r"",
        views.dashboard,
        name="administration_dashboard",
    ),
    path(
        "event/<int:pk>/update/",
        user_can_add_events(views.update_event),
        name="administration_event_update",
    ),
    path(
        "event/<int:pk>/delete/",
        user_can_add_events(
            DeleteView.as_view(
                model=Event,
                template_name="administration/event_confirm_delete.haml",
                success_url=reverse_lazy("administration_dashboard"),
            )
        ),
        name="administration_event_delete",
    ),
]
