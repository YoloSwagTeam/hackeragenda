# encoding: utf-8

import sys
import json
import calendar
import requests

from urllib2 import urlopen
from datetime import datetime, date, timedelta
from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse
from icalendar import Calendar
from icalendar import Event as icalendarEvent
from optparse import make_option
from HTMLParser import HTMLParser

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event

# Needed for BxLUG
reload(sys)
sys.setdefaultencoding("utf-8")


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='No debug output'),
    )

    def handle(self, *args, **options):
        if args:
            sources = args
        else:
            sources = [
                "afpyro",
                "agenda_du_libre_be",
                "agile_belgium",
                "aws_user_group_belgium",
                "belgian_angularjs",
                "belgian_nodejs_user_group",
                "belgian_puppet_user_group",
                "brussels_data_science_meetup",
                "bescala",
                "bhackspace",
                "bigdata_be",
                "brussels_cassandra_users",
                "brussels_wordpress",
                "bxlug",
                "constantvzw",
                "docker_belgium",
                "ember_js_brussels",
                "foam",
                "hsbxl",
                "incubhacker",
                "laravel_brussels",
                "les_mardis_de_l_agile",
                "mongodb_belgium",
                "neutrinet",
                "okno",
                "opengarage",
                "opentechschool",
                "owaspbe",
                "phpbenelux",
                "ruby_burgers",
                "https://urlab.be/hackeragenda.json",
                "voidwarranties",
                "webrtc",
                "whitespace",
                # "wolfplex",
            ]

        for source in sources:
            try:
                with transaction.commit_on_success():
                    if source.startswith(('http://', 'https://')):
                        json_api(source, options)
                        continue

                    if source not in globals():
                        print >>sys.stderr, "Error: %s is not an available source" % source
                        return

                    globals()[source](options)
            except Exception as e:
                import traceback
                traceback.print_exc(file=sys.stdout)
                print e


def afpyro(options={}):
    # clean events
    Event.objects.filter(source="afpyro").delete()

    soup = BeautifulSoup(urlopen("http://afpyro.afpy.org/").read())
    filtering = lambda x: x['href'][:7] == '/dates/' and '(BE)' in x.text
    for link in filter(filtering, soup('a')):
        datetuple = map(int, link['href'].split('/')[-1].split('.')[0].split('_'))
        event = Event.objects.create(
            title=link.text,
            source="afpyro",
            url="http://afpyro.afpy.org" + link['href'],
            start=datetime(*datetuple)
        )
        if not options['quiet']:
            print "Adding %s [%s]" % (event.title.encode("Utf-8"), event.source)


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
            print "Adding %s [%s] (%s)..." % (event["SUMMARY"].encode("Utf-8"), "agenda_du_libre_be", event["LOCATION"].encode("Utf-8"))


def agile_belgium(options):
    return generic_meetup("agile_belgium", "Agile-Belgium", options)


def aws_user_group_belgium(options):
    return generic_meetup("aws_user_group_belgium", "AWS-User-Group-Belgium", options)


def belgian_angularjs(options):
    return generic_meetup("belgian_angularjs", "The-Belgian-AngularJS-Meetup-Group", options)


def belgian_nodejs_user_group(options):
    return generic_meetup("belgian_nodejs_user_group", "Belgian-node-js-User-Group", options)


def belgian_puppet_user_group(options):
    return generic_meetup("belgian_puppet_user_group", "Belgian-Puppet-User-Group", options)


def bescala(options):
    return generic_meetup("bescala", "BeScala", options)


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
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), "bhackspace", location.encode("Utf-8"))


def bigdata_be(options):
    return generic_meetup("bigdata_be", "bigdatabe", options)


def brussels_cassandra_users(options):
    return generic_meetup("brussels_cassandra_users", "Brussels-Cassandra-Users", options)


def brussels_data_science_meetup(options):
    return generic_meetup("brussels_data_science_meetup", "Brussels-Data-Science-Community-Meetup", options)


def brussels_wordpress(options):
    return generic_meetup("brussels_wordpress", "wp-bru", options)


def bxlug(options):
    Event.objects.filter(source="bxlug").delete()

    soup = BeautifulSoup(urlopen("http://www.bxlug.be/spip.php?page=agenda-zpip"))
    for entry in soup('article', 'evenement'):
        # [:-1] => ignore timezones, because sqlite doesn't seem to like it
        start = parse(entry('meta', itemprop='startDate')[0]['content'][:-1])
        end = parse(entry('meta', itemprop='endDate')[0]['content'][:-1])
        title = entry('span', itemprop='name')[0].text
        url = "http://www.bxlug.be/" + entry('a', itemprop='url')[0]['href']
        event = Event.objects.create(
            title=title,
            source="bxlug",
            url=url,
            start=start,
            end=end
        )

        if not options["quiet"]:
            print "Adding %s [%s]" % (event.title, event.source)


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
            elif len(data) == 7:
                start = parse("%s %s %s" % tuple(data[:3]))
                end = parse("%s %s %s" % tuple(data[4:]))
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
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), "constantvzw", location.encode("Utf-8") if location else "")


def docker_belgium(options):
    return generic_meetup("docker_belgium", "Docker-Belgium", options)


def ember_js_brussels(options):
    return generic_meetup("ember_js_brussels", "Ember-js-Brussels", options)


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

        event = Event.objects.create(
            title=title.text,
            source="foam",
            url='http://fo.am' + link,
            start=start,
            end=end
        )

        if "FoAM Apéro" in event.title:
            event.tags.add("meeting")

        if not options["quiet"]:
            print "Adding %s [foam]" % title.text.encode("Utf-8")


def hsbxl(options):
    # clean events
    Event.objects.filter(source="hsbxl").delete()

    today = date.today() - timedelta(days=6 * 30)

    data = json.load(urlopen("https://hackerspace.be/Special:Ask/-5B-5BCategory:TechTue-7C-7CEvent-5D-5D-20-5B-5BEnd-20date::-3E%s-2D%s-2D%s-20-5D-5D/-3FStart-20date/-3FEnd-20date/-3FLocation/format%%3Djson/sort%%3D-5BStart-20date-5D/order%%3Dasc/offset%%3D0'" % (today.year, today.month, today.day)))

    for event in data["results"].values():
        db_event = Event.objects.create(
            title=event["fulltext"],
            source="hsbxl",
            url=event["fullurl"],
            start=datetime.fromtimestamp(int(event["printouts"]["Start date"][0])),
            end=datetime.fromtimestamp(int(event["printouts"]["End date"][0])),
            location=event["printouts"]["Location"][0]["fulltext"]
        )

        if "TechTue" in event["fulltext"]:
            db_event.tags.add("meeting")

        if not options["quiet"]:
            print "Adding %s [%s] (%s)..." % (event["fulltext"].encode("Utf-8"), "hsbxl", event["printouts"]["Location"][0]["fulltext"].encode("Utf-8"))


def incubhacker(options):
    # clean events
    Event.objects.filter(source="incubhacker").delete()

    now = calendar.timegm(datetime.now().utctimetuple())

    # 2 magics numbers are from a reverse of the incubhacker calendar api
    for event in json.load(urlopen("http://www.incubhacker.be/index.php/component/gcalendar/jsonfeed?format=raw&gcid=2&start=%s&end=%s" % (now - 1187115, now + 2445265))):
        title = event["title"]
        url = "http://www.incubhacker.be" + event["url"]
        start = parse(event["start"]).replace(tzinfo=None)
        end = parse(event["end"]).replace(tzinfo=None)

        event = Event.objects.create(
            title=title,
            source="incubhacker",
            url=url,
            start=start,
            end=end
        )

        if event.title.strip() in ("INCUBHACKER", "Réunion normale"):
            event.tags.add("meeting")

        if not options["quiet"]:
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), "incubhacker", "")


def laravel_brussels(options):
    return generic_meetup("laravel_brussels", "Laravel-Brussels", options)


def les_mardis_de_l_agile(options):
    return generic_meetup("les_mardis_de_l_agile", "Les-mardis-de-lagile-Bruxelles", options)


def mongodb_belgium(options):
    return generic_meetup("mongodb_belgium", "MongoDB-Belgium", options)


def neutrinet(options):
    # clean events
    Event.objects.filter(source="neutrinet").delete()

    soup = BeautifulSoup(urlopen("http://neutrinet.be/index.php?title=Main_Page").read())

    if not soup.table.table.tr.find('table', 'wikitable'):
        return

    for event in filter(lambda x: x, map(lambda x: x('td'), soup.table.table.tr.find('table', 'wikitable')('tr'))):
        title = event[0].text
        url = "https://neutrinet.be" + event[0].a["href"]
        start = parse(event[1].text)
        location = event[2].text

        event = Event.objects.create(
            title=title,
            source="neutrinet",
            url=url,
            start=start,
            location=location.strip() if location else None
        )

        if "Meeting" in event.title:
            event.tags.add("meeting")

        if not options["quiet"]:
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), "neutrinet", location.encode("Utf-8"))


def okno(options):
    Event.objects.filter(source="okno").delete()
    soup = BeautifulSoup(urlopen("http://www.okno.be/events/").read())

    for entry in soup('div', 'switch-events'):
        datetuple = map(int, entry('span', 'date-display-single')[0].text.split('.'))
        title = entry('span', 'field-content')[0].text
        link = "http://www.okno.be" + entry('a')[0]['href']
        Event.objects.create(
            title=title,
            source="okno",
            url=link,
            start=datetime(*datetuple)
        )

        if not options["quiet"]:
            print "Adding %s [okno]" % (title.encode("Utf-8"))


def opengarage(options):
    return generic_meetup("opengarage", "OpenGarage", options)


def opentechschool(options):
    return generic_meetup("opentechschool", "OpenTechSchool-Brussels", options)


def owaspbe(options):
    Event.objects.filter(source="owaspbe").delete()
    soup = BeautifulSoup(urlopen("http://www.eventbrite.com/o/owasp-belgium-chapter-1865700117").read())

    for event in soup.findAll("div", attrs= {"class" : "event_row vevent clrfix"}):
        title = event.find("span", attrs = {"class" : "summary"}).string
        location = event.find("span", attrs = {"class" : "street-address microformats_only"}).text
        start = event.find("span", attrs = {"class" : "dtstart microformats_only"}).text
        end = event.find("span", attrs = {"class" : "dtend microformats_only"}).text
        url = event.find("a", attrs = {"class" : "url"})['href']

        Event.objects.create(
            title=title,
            source="owaspbe",
            start=start,
            end=end,
            url=url,
            location=location
        )
        if not options["quiet"]:
            print "Adding %s [owaspbe]" % (title.encode("Utf-8"))

def phpbenelux(options):
    return generic_meetup("phpbenelux", "phpbenelux", options)


def ruby_burgers(options):
    return generic_meetup("ruby_burgers", "ruby_burgers-rb", options)


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
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), "voidwarranties", "")


def webrtc(options):
    return generic_meetup("webrtc", "WebRTC-crossingborders", options)


def whitespace(options):
    # clean events
    Event.objects.filter(source="whitespace").delete()

    soup = BeautifulSoup(urlopen("http://www.0x20.be/Main_Page").read())

    for event in soup.ul('li'):
        if event.text == 'More...':
            continue
        title = event.a.text
        url = "http://www.0x20.be" + event.a["href"]
        if "-" in event.b.text[:-1]:
            start, end = map(lambda x: parse(x.strip()), event.b.text[:-1].split("-"))
        else:
            start = parse(event.b.text[:-1])
            end = None
        location = event('a')[1].text

        Event.objects.create(
            title=title,
            source="whitespace",
            url=url,
            start=start,
            end=end,
            location=location.strip() if location else None
        )

        if not options["quiet"]:
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), "whitespace", location.encode("Utf-8"))


def wolfplex(options):
    # clean events
    Event.objects.filter(source="wolfplex").delete()

    html_parser = HTMLParser()

    soup = BeautifulSoup(urlopen("http://www.wolfplex.org/wiki/Main_Page").read())

    events = soup.find("div", id="accueil-agenda").dl

    for date_info, event in zip(events('dt'), events('dd')[1::2]):
        if event.span:
            event.span.clear()

        title = html_parser.unescape(event.text)
        base_domain = "http://www.wolfplex.org" if not event.a["href"].startswith("http") else ""
        url = (base_domain + event.a["href"]) if event.a else "http://www.wolfplex.org"
        start = parse(date_info.span["title"])

        if "@" in title:
            title, location = title.split("@", 1)
        else:
            location = None

        Event.objects.create(
            title=title,
            source="wolfplex",
            url=url,
            start=start,
            location=location
        )

        if not options["quiet"]:
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), "wolfplex", location.encode("Utf-8") if location else "")


def json_api(url, options):
    """
    Generic function to add events from an urls respecting the json api
    """
    data = json.load(urlopen(url))

    # clean events
    Event.objects.filter(source=data['org']).delete()

    for event in data['events']:
        Event.objects.create(
            title=event['title'],
            source=data['org'],
            url=event['url'],
            start=parse(event['start']).replace(tzinfo=None),
            end=parse(event['end']).replace(tzinfo=None) if 'end' in event else None,
            all_day=event['all_day'] if 'all_day' in event else None,
            location=event['location'] if 'location' in event else None,
        )

        if not options["quiet"]:
            print "Adding %s [%s] (%s)..." % (event['title'].encode("Utf-8"), data['org'], event.get('location', '').encode("Utf-8"))


def generic_meetup(source, meetup_name, options):
    Event.objects.filter(source=source, start__gte=datetime.now()).delete()

    data = Calendar.from_ical(requests.get("http://www.meetup.com/{}/events/ical/".format(meetup_name)).content)

    for event in data.walk():
        if not isinstance(event, icalendarEvent):
            continue

        title = event.get("SUMMARY", None)
        start = event.get("DTSTART", None)

        if None in (title, start):
            continue

        if event.get("URL") and Event.objects.filter(url=event["url"]):
            continue

        Event.objects.create(
            title=title.encode("Utf-8"),
            source=source,
            url=event.get("URL", ""),
            start=start.dt.replace(tzinfo=None),
            location=event.get("LOCATION", "").encode("Utf-8")
        )

        if not options["quiet"]:
            print "Adding %s [%s] (%s)..." % (title.encode("Utf-8"), source, event.get("LOCATION", "").encode("Utf-8"))
