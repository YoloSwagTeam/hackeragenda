from datetime import datetime

from django.contrib.syndication.views import Feed

from .models import Event


class NextEventsFeed(Feed):
    title = "Events"
    link = ""
    description = "Next events"

    def items(self):
        return Event.objects.filter(start__gte=datetime.now).order_by("start")

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
