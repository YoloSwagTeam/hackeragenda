from django.views.generic.edit import CreateView

from events.models import Event


class CreateEvent(CreateView):
    model = Event
    template_name = "administration/dashboard.haml"
