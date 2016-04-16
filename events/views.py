import json
from datetime import timedelta, datetime

from django.http import HttpResponse
from django.conf import settings
from django.views.generic import ListView, TemplateView, MonthArchiveView

from taggit.models import Tag

from administration.models import Source

from .models import Event
from .management.commands.fetch_events import SOURCES_OPTIONS
from .utils import filter_events


class HomeView(TemplateView):
    template_name = "home-%s.haml" % settings.AGENDA

    def get_sources_from_db(self):
        return [(x.name, {
            "agenda": x.agenda,
            "bg": x.border_color,
            "fg": x.text_color,
            "description": x.description,
            "url": x.url,
        }) for x in Source.objects.all()]

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context["sources"] = sorted(filter(lambda x: x[1]["agenda"] == settings.AGENDA, SOURCES_OPTIONS.items() + self.get_sources_from_db()), key=lambda x: x[0])
        context["tags"] = [x[0] for x in Tag.objects.filter(taggit_taggeditem_items__object_id__in=[x[0] for x in Event.objects.filter(agenda=settings.AGENDA).values_list("id")]).distinct().values_list("name").order_by("name")]
        context["predefined_filters"] = settings.PREDEFINED_FILTERS
        context["predefined_filters_json"] = dict(settings.PREDEFINED_FILTERS)
        return context


class EventListView(ListView):
    template_name = "events.haml"
    queryset = Event.objects.filter(agenda=settings.AGENDA).order_by("start")

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context["object_list"] = context["object_list"].filter(start__gte=datetime.now())
        context["object_list"] = filter_events(self.request, context["object_list"])
        return context


def get_events_in_json(request):
    return HttpResponse(json.dumps(map(event_to_fullcalendar_format, filter_events(request=request, queryset=Event.objects.filter(agenda=settings.AGENDA)))), content_type="application/json")


def get_events_for_map_in_json(request):
    events = []
    queryset = Event.objects.filter(agenda=settings.AGENDA, start__gte=datetime.now(), lon__isnull=False, lat__isnull=False).filter(start__lt=(datetime.now() + timedelta(days=31)))

    for event in filter_events(request=request, queryset=queryset):
        in_x_days = (event.start - datetime.now()).days

        if in_x_days <= 1:
            color = "red"
        elif in_x_days <= 7:
            color = "orange"
        else:
            color = "green"

        events.append({
            "title": "%s [%s]" % (event.title, event.source),
            "url": event.url,
            "lat": event.lat,
            "lon": event.lon,
            "color": color,
            "days": in_x_days,
            "start": str(event.start),
            "location": event.location,
        })

    return HttpResponse(json.dumps(events), content_type="application/json")

def event_to_fullcalendar_format(event):
    to_return = {
        "title": "%s [%s]" % (event.title, event.source),
        "url": event.url,
        "color": event.calendar_border_color,
        "textColor": event.calendar_text_color,
        "allDay": event.all_day,
    }

    start, end = event.start, event.end
    if end is None:
        end = start + timedelta(hours=3)

    if event.all_day:
        to_return["start"] = start.strftime("%F")
        if start.date() != end.date():
            to_return["end"] = end.strftime("%F")
    else:
        to_return["start"] = start.strftime("%F %X")
        to_return["end"] = end.strftime("%F %X")

    return to_return


class EventMonthArchiveView(MonthArchiveView):
    model = Event
    date_field = "start"
    month_format = "%m"
    template_name = "events/event_archive_month.haml"
