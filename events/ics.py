from datetime import timedelta

from icalendar import Calendar, Event as ICSEvent

from django.http import HttpResponse
from .models import Event

def get_ics_of_events(request):
    cal = Calendar()
    cal.add('prodid', 'Hacker Agenda')
    cal.add('version', '2.0')

    for event in Event.objects.all():
        ics_event = ICSEvent()
        ics_event.add('summary', '%s [%s]' % (event.title, event.source))
        ics_event.add('dtstart', event.start)
        if event.start.hour == 0 and event.start.minute == 0:
            ics_event.add('dtstart', event.start.date())
        else:
            if event.end:
                ics_event.add('dtend', event.end)
            else:
                ics_event.add('dtend', event.start + timedelta(hours=3))
        ics_event.add('dtstamp', event.start)
        ics_event['uid'] = event.url

        cal.add_component(ics_event)

    return HttpResponse(cal.to_ical(), mimetype="text/calendar")
