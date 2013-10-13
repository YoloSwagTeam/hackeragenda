from urllib2 import urlopen
from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse
from feedparser import parse as feed_parse

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event


class Command(BaseCommand):
    def handle(self, *args, **options):
        for source in [urlab, neutrinet, hsbxl, agenda_du_libre_be, constantvzw]:
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


def agenda_du_libre_be():
    # clean events
    Event.objects.filter(source="agenda_du_libre_be").delete()

    for event in feed_parse("http://agendadulibre.be/rss.php?region=all").entries:
        Event.objects.create(
            title=event.title,
            source="agenda_du_libre_be",
            url=event.link,
            start=parse(event.updated).replace(tzinfo=None),
            location=event.summary.split(":")[0],
            text_color="white",
        )

        print "adding %s [%s] (%s)..." % (event.title, "agenda_du_libre_be", event.summary.split(":")[0])

def constantvzw():
    Event.objects.filter(source="constantvzw").delete()

    soup = BeautifulSoup(urlopen("http://www.constantvzw.org/site/").read())

    for event in soup.find("div", id="flow")("div", recursive=False)[:-1]:
        title = event('a')[1].text
        url = "http://www.constantvzw.org/site/" + event('a')[1]["href"]

        if len(event.span.text.split(" @ ")) == 2:
            time, location = event.span.text.split(" @ ")
        else:
            time = event.span.text.split("@")[0].strip()
            location = None

        if time.startswith("From "):
            data = time.split(" ")[1:]
            if len(data) == 4:
                start = parse("%s %s" % (data[0], data[3]))
                end = parse("%s %s" % (data[2], data[3]))
            else:
                start = parse("%s %s" % (data[0], data[1]))
                end = parse("%s %s" % (data[3], data[4]))
        else:
            start = parse(time).replace(tzinfo=None)
            end = None

        Event.objects.create(
            title=title,
            source="constantvzw",
            url=url,
            start=start,
            end=end,
            location=location,
            color="#D2C7BA",
            text_color="black",
        )

        print "adding %s [%s] (%s)..." % (title, "constantvzw", location)
