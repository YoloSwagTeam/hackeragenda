from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event


class Command(BaseCommand):
    def handle(self, *args, **options):
        for source in [urlab, neutrinet]:
            with transaction.commit_on_success():
                source()


def urlab():
    # clean events
    Event.objects.filter(source="urlab").delete()

    soup = BeautifulSoup(urlopen("https://wiki.urlab.be/Main_Page").read())

    for event in filter(lambda x: x, map(lambda x: x('td'), soup('table', 'wikitable')[0]('tr'))):
        title = event[0].text
        url = "https://wiki.urlab.be" + event[0].a["href"]
        start = parse(event[1].text)
        location = event[2].text

        Event.objects.create(
            title=title,
            source="urlab",
            url=url,
            start=start,
            location=location,
            color="pink",
            text_color="black",
        )

        print "adding %s [%s] (%s)..." % (title, "urlab", location)


def neutrinet():
    # clean events
    Event.objects.filter(source="neutrinet").delete()

    soup = BeautifulSoup(urlopen("http://neutrinet.be/index.php?title=Main_Page").read())

    for event in filter(lambda x: x, map(lambda x: x('td'), soup('table', 'wikitable')[0]('tr'))):
        title = event[0].text
        url = "https://neutrinet.be" + event[0].a["href"]
        start = parse(event[1].text)
        location = event[2].text

        Event.objects.create(
            title=title,
            source="neutrinet",
            url=url,
            start=start,
            location=location,
            color="dark blue",
            text_color="white",
        )

        print "adding %s [%s] (%s)..." % (title, "neutrinet", location)
