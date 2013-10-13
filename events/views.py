import json
from django.http import HttpResponse

from .models import Event

def get_events_in_json(request):
    return HttpResponse(json.dumps([{
        "title": "%s [%s]" % (x.title, x.source),
        "start": x.start.strftime("%F"),
        "color": x.color,
        "textColor": x.text_color,
        "url": x.url,
    } for x in Event.objects.all()]))
