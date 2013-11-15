import sys
import json
import calendar

from urllib2 import urlopen
from datetime import datetime, date, timedelta
from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse
from icalendar import Calendar
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='No debug output'),
        )

    def handle(self, *args, **options):
        for source in [
                       urlab,
                       foam,
                       neutrinet,
                       hsbxl,
                       agenda_du_libre_be,
                       constantvzw,
                       bhackspace,
                       incubhacker,
                       opengarage,
                       whitespace,
                       voidwarranties,
                      ]:
            try:
                with transaction.commit_on_success():
                    source(options)
            except Exception as e:
                import traceback
                traceback.print_exc(file=sys.stdout)
                print e


def urlab(options):
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
            location=location.strip() if location else None
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "urlab", location.encode("Utf-8"))


def foam(options):
    Event.objects.filter(source="foam").delete()

    soup = BeautifulSoup(urlopen("http://fo.am/events/").read())

    for line in soup.find('table', 'eventlist')('tr')[1:]:
        title, event_date = line('td')

        link = title.a['href']

        dates = map(parse, event_date.text.split('-'))
        if len(dates) == 2:
            start, end = dates
        else:
            start, end = dates[0], None

        Event.objects.create(
            title=title.text,
            source="foam",
            url='http://fo.am' + link,
            start=start,
            end=end
        )
        if not options["quiet"]:
            print "Adding %s [foam]" % title.text.encode("Utf-8")


def neutrinet(options):
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
            location=location.strip() if location else None
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "neutrinet", location.encode("Utf-8"))


def hsbxl(options):
    # clean events
    Event.objects.filter(source="hsbxl").delete()

    today = date.today() - timedelta(days=6 * 30)

    data = json.load(urlopen("https://hackerspace.be/Special:Ask/-5B-5BCategory:TechTue-7C-7CEvent-5D-5D-20-5B-5BEnd-20date::-3E%s-2D%s-2D%s-20-5D-5D/-3FStart-20date/-3FEnd-20date/-3FLocation/format%%3Djson/sort%%3D-5BStart-20date-5D/order%%3Dasc/offset%%3D0'" % (today.year, today.month, today.day)))

    for event in data["results"].values():
        Event.objects.create(
            title=event["fulltext"],
            source="hsbxl",
            url=event["fullurl"],
            start=datetime.fromtimestamp(int(event["printouts"]["Start date"][0])),
            end=datetime.fromtimestamp(int(event["printouts"]["End date"][0])),
            location=event["printouts"]["Location"][0]["fulltext"]
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (event["fulltext"].encode("Utf-8"), "hsbxl", event["printouts"]["Location"][0]["fulltext"].encode("Utf-8"))


def agenda_du_libre_be(options):
    # clean events
    Event.objects.filter(source="agenda_du_libre_be").delete()

    data = Calendar.from_ical(urlopen("http://www.agendadulibre.be/ical.php?region=all").read())

    for event in data.walk()[1:]:
        Event.objects.create(
            title=event["SUMMARY"].encode("Utf-8"),
            source="agenda_du_libre_be",
            url=event["URL"],
            start=event["DTSTART"].dt.replace(tzinfo=None),
            location=event["LOCATION"].encode("Utf-8")
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (event["SUMMARY"].encode("Utf-8"), "agenda_du_libre_be", event["LOCATION"].encode("Utf-8"))


def constantvzw(options):
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
            location=location.strip() if location else None
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "constantvzw", location.encode("Utf-8") if location else "")


def bhackspace(options):
    # clean events
    Event.objects.filter(source="bhackspace").delete()

    soup = BeautifulSoup(urlopen("http://wiki.bhackspace.be/index.php/Main_Page").read())

    if soup.table.find('table', 'table') is None:
        return

    for event in soup.find('table', 'table')('tr')[1:]:
        title = event.a.text
        url = "http://wiki.bhackspace.be" + event.a["href"]
        start = parse(event('td')[1].text)
        location = event('td')[2].text

        Event.objects.create(
            title=title,
            source="bhackspace",
            url=url,
            start=start,
            location=location.strip() if location else None
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "bhackspace", location.encode("Utf-8"))


def incubhacker(options):
    # clean events
    Event.objects.filter(source="incubhacker").delete()

    now = calendar.timegm(datetime.now().utctimetuple())

    # 2 magics numbers are from a reverse of the incubhacker calendar api
    for event in json.load(urlopen("http://www.incubhacker.be/index.php/agenda/jsonfeed?format=raw&gcid=2&start=%s&end=%s" % (now - 1187115, now + 2445265))):
        title = event["title"]
        url = "http://www.incubhacker.be" + event["url"]
        start = parse(event["start"]).replace(tzinfo=None)
        end = parse(event["end"]).replace(tzinfo=None)

        Event.objects.create(
            title=title,
            source="incubhacker",
            url=url,
            start=start,
            end=end
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "incubhacker", "")


def opengarage(options):
    # clean events
    Event.objects.filter(source="opengarage").delete()

    soup = BeautifulSoup(urlopen("http://www.meetup.com/OpenGarage/").read())

    for event in soup.find('ul', id='ajax-container')('li'):
        if event.find('li', 'dateTime') is None or event.find('li', 'dateTime').time is None:
            continue
        title = event.a.text
        url = event.a["href"]
        start = parse(event.find('li', 'dateTime').time['datetime']).replace(tzinfo=None)

        Event.objects.create(
            title=title,
            source="opengarage",
            url=url,
            start=start
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "opengarage", "")


def whitespace(options):
    # clean events
    Event.objects.filter(source="whitespace").delete()

    soup = BeautifulSoup(urlopen("http://www.0x20.be/Main_Page").read())

    for event in soup.ul('li'):
        title = event.a.text
        url = "http://www.0x20.be" + event.a["href"]
        start = parse(event.b.text[:-1])
        location = event('a')[1].text

        Event.objects.create(
            title=title,
            source="whitespace",
            url=url,
            start=start,
            location=location.strip() if location else None
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "whitespace", location.encode("Utf-8"))


def voidwarranties(options):
    # clean events
    Event.objects.filter(source="voidwarranties").delete()

    data = Calendar.from_ical(urlopen("http://voidwarranties.be/index.php/Special:Ask/-5B-5BCategory:Events-5D-5D/-3FHas-20start-20date=start/-3FHas-20end-20date=end/-3FHas-20coordinates=location/format=icalendar/title=VoidWarranties/description=Events-20at-20http:-2F-2Fvoidwarranties.be/limit=500").read())

    for event in data.walk()[1:]:
        title = str(event["SUMMARY"])
        url = event["URL"]
        start = event["DTSTART"].dt if event.get("DTSTART") else event["DTSTAMP"].dt
        end = event["DTEND"].dt if event.get("DTSTART") else None

        Event.objects.create(
            title=title,
            source="voidwarranties",
            url=url,
            start=start,
            end=end
        )

        if not options["quiet"]:
            print "adding %s [%s] (%s)..." % (title.encode("Utf-8"), "voidwarranties", "")
