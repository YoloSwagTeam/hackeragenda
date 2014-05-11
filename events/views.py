import json
from datetime import timedelta, datetime

from django.http import HttpResponse
from django.views.generic import ListView

from taggit.models import Tag

from .models import Event
from .colors import COLORS


def filter_events(request, queryset):
    if request.GET.getlist("source"):
        queryset = queryset.filter(source__in=request.GET.getlist("source"))

    if request.GET.getlist("exclude_source"):
        queryset = queryset.exclude(source__in=request.GET.getlist("exclude_source"))

    if request.GET.getlist("tag"):
        queryset = queryset.filter(tags__name__in=request.GET.getlist("tag"))

    if request.GET.getlist("exclude_tag"):
        queryset = queryset.exclude(tags__name__in=request.GET.getlist("exclude_tag"))

    return queryset


class EventListView(ListView):
    template_name = "home.haml"
    queryset = Event.objects.filter(start__gte=datetime.now).order_by("start")

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context["sources"] = sorted(COLORS.items(), key=lambda x: x[0])
        context["tags"] = map(lambda x: x[0], Tag.objects.order_by("name").values_list("name"))
        filter_events(self.request, context["object_list"])
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
