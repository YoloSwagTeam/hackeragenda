from datetime import timedelta

from icalendar import Calendar, Event as ICSEvent

from django.http import HttpResponse
from django.conf import settings

from .models import Event
from .utils import filter_events


def get_ics_of_events(request):
    cal = Calendar()
    cal.add('prodid', 'Hacker Agenda')
    cal.add('version', '2.0')

    for event in filter_events(request=request, queryset=Event.objects.filter(agenda=settings.AGENDA)):
        ics_event = ICSEvent()
        ics_event.add('summary', '%s [%s]' % (event.title, event.source))
        if event.start.hour == 0 and event.start.minute == 0:
            ics_event.add('dtstart', event.start.date())
        else:
            ics_event.add('dtstart', event.start)
            if event.end:
                ics_event.add('dtend', event.end)
            else:
                ics_event.add('dtend', event.start + timedelta(hours=3))
        ics_event.add('dtstamp', event.start)
        ics_event['uid'] = event.url

        cal.add_component(ics_event)

    return HttpResponse(cal.to_ical(), mimetype="text/calendar")
