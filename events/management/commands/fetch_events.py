from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event


class Command(BaseCommand):
    def handle(self, *args, **options):
        for source in [urlab, neutrinet, hsbxl]:
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
            color="DarkBlue",
            text_color="white",
        )

        print "adding %s [%s] (%s)..." % (title, "neutrinet", location)


def hsbxl():
    # clean events
    Event.objects.filter(source="hsbxl").delete()

    soup = BeautifulSoup(urlopen("http://www.hackerspace.be/Hackerspace_Brussels").read())

    for event in soup.table.table('ul'):
        title = event.a.text
        url = "http://www.hackerspace.be" + event.a["href"]
        if len(event.b.text.split(" - ")) == 2:
            start, end = event.b.text.split(" - ")
            start, end = parse(start), parse(end[:-1])
        else:
            start, end = (parse(event.b.text[:-1]), None)
        location = event('a')[1].text

        Event.objects.create(
            title=title,
            source="hsbxl",
            url=url,
            start=start,
            end=end,
            location=location,
            color="Green",
            text_color="white",
        )

        print "adding %s [%s] (%s)..." % (title, "hsbxl", location)
