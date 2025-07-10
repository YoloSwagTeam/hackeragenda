from datetime import datetime

from django.conf import settings
from django.contrib.syndication.views import Feed

from .models import Event
from .utils import filter_events


class NextEventsFeed(Feed):
    title = "Events"
    link = ""
    description = "Next events"

    def items(self):
        return filter_events(
            request=self.request,
            queryset=Event.objects.filter(
                start__gte=datetime.now, agenda=settings.AGENDA
            ).order_by("start"),
        )

    def get_object(self, request):
        # youhou, dirty hack to have access to request in items()
        self.request = request
        return None

    def item_title(self, item):
        return "%s [%s]" % (item.title, item.source)

    def item_description(self, item):
        description = "%s: %s" % (item.source, item.title)
        if item.location:
            description += " at %s" % item.location
        return description

    def item_link(self, item):
        return item.url

    def item_author_name(self, item):
        return item.source

    def item_pubdate(self, item):
        return item.start
