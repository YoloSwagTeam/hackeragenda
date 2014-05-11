import json
from datetime import timedelta, datetime

from django.http import HttpResponse
from django.conf import settings
from django.views.generic import ListView, TemplateView

from taggit.models import Tag

from .models import Event
from .colors import COLORS
from .utils import filter_events


class HomeView(TemplateView):
    template_name = "home.haml"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["sources"] = sorted(COLORS.items(), key=lambda x: x[0])
        context["tags"] = map(lambda x: x[0], Tag.objects.order_by("name").values_list("name"))
        context["predefined_filters"] = settings.PREDEFINED_FILTERS
        context["predefined_filters_json"] = dict(settings.PREDEFINED_FILTERS)
        return context


class EventListView(ListView):
    template_name = "events.haml"
    queryset = Event.objects.filter(start__gte=datetime.now).order_by("start")

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context["object_list"] = filter_events(self.request, context["object_list"])
        return context


def get_events_in_json(request):
    return HttpResponse(json.dumps(map(event_to_fullcalendar_format, filter_events(request=request, queryset=Event.objects.all()))), mimetype="application/json")


def event_to_fullcalendar_format(event):
    to_return = {
        "title": "%s [%s]" % (event.title, event.source),
        "color": event.background_color,
        "textColor": event.text_color,
        "url": event.url,
    }

    if event.start.hour == 0 and event.start.minute == 0:
        to_return["start"] = event.start.strftime("%F")
    else:
        to_return["start"] = event.start.strftime("%F %X")
        to_return["allDay"] = False
        if event.end:
            to_return["end"] = event.end.strftime("%F %X")
        else:
            to_return["end"] = (event.start + timedelta(hours=3)).strftime("%F %X")

    return to_return
