import json
from datetime import timedelta, datetime

from django.http import HttpResponse
from django.views.generic import ListView

from taggit.models import Tag

from .models import Event
from .colors import COLORS


def filter_events(request, context):
    sources = request.GET.getlist("source", map(lambda x: x[0], context["sources"]))
    context["object_list"] = context["object_list"].filter(source__in=sources)


class EventListView(ListView):
    template_name = "home.haml"
    queryset = Event.objects.filter(start__gte=datetime.now).order_by("start")

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context["sources"] = sorted(COLORS.items(), key=lambda x: x[0])
        context["tags"] = Tag.objects.order_by("name").values_list("name")
        filter_events(self.request, context)
        return context


def get_events_in_json(request):
    return HttpResponse(json.dumps(map(event_to_fullcalendar_format, Event.objects.all())), mimetype="application/json")


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
