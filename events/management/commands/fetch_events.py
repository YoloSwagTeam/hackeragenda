# encoding: utf-8

import sys
import json
import calendar
import requests
import time

from urllib2 import urlopen
from datetime import datetime, date, timedelta
from collections import OrderedDict

from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse
from icalendar import Calendar
from icalendar import Event as icalendarEvent
from optparse import make_option
from HTMLParser import HTMLParser

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event


SOURCES_FUNCTIONS = OrderedDict()

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='No debug output'),
    )

    def handle(self, *args, **options):
        def create_event(**detail):
            res = Event.objects.create(source=source, **detail)
            if not options.get('quiet', True):
                print "[%s] %s (%s)"%(res.source, res.title, res.start)
            return res

        sources = SOURCES_FUNCTIONS.keys() if not args else args

        for source in sources:
            try:
                with transaction.commit_on_success():
                    Event.objects.filter(source=source).delete()
                    SOURCES_FUNCTIONS[source](create_event)
                    if not options.get('quiet', True):
                        print " === Finished for " + source

            except Exception as e:
                import traceback
                traceback.print_exc(file=sys.stdout)
                print e


def event_source(func, org_name=None):
    if org_name is None:
        org_name = func.__name__.lower()

    print("Event source detected: " + org_name)
    SOURCES_FUNCTIONS[org_name] = func
    return func


def json_api(org_name, url):
    def fetch(create_event):
        """
        Generic function to add events from an urls respecting the json api
        """
        data = json.load(urlopen(url))
        for event in data['events']:
            create_event(
                title=event['title'],
                url=event['url'],
                start=parse(event['start']).replace(tzinfo=None),
                end=parse(event['end']).replace(tzinfo=None) if 'end' in event else None,
                all_day=event['all_day'] if 'all_day' in event else None,
                location=event['location'] if 'location' in event else None,
            )
    return event_source(fetch, org_name)


def generic_meetup(org_name, meetup_name):
    def fetch(create_event):
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

            create_event(
                title=title.encode("Utf-8"),
                url=event.get("URL", ""),
                start=start.dt.replace(tzinfo=None),
                location=event.get("LOCATION", "").encode("Utf-8")
            )
    return event_source(fetch, org_name)


@event_source
def afpyro(create_event):
    soup = BeautifulSoup(urlopen("http://afpyro.afpy.org/").read())
    filtering = lambda x: x['href'][:7] == '/dates/' and '(BE)' in x.text
    for link in filter(filtering, soup('a')):
        datetuple = map(int, link['href'].split('/')[-1].split('.')[0].split('_'))
        create_event(
            title=link.text, 
            start=datetime(*datetuple), 
            url="http://afpyro.afpy.org" + link['href']
        )


@event_source
def agenda_du_libre_be(create_event):
    data = Calendar.from_ical(urlopen("http://www.agendadulibre.be/ical.php?region=all").read())

    for event in data.walk()[1:]:
        create_event(
            title=event["SUMMARY"].encode("Utf-8"),
            url=event["URL"],
            start=event["DTSTART"].dt.replace(tzinfo=None),
            location=event["LOCATION"].encode("Utf-8")
        )


generic_meetup("agile_belgium", "Agile-Belgium")


generic_meetup("aws_user_group_belgium", "AWS-User-Group-Belgium")


generic_meetup("belgian_angularjs", "The-Belgian-AngularJS-Meetup-Group")


generic_meetup("belgian_nodejs_user_group", "Belgian-node-js-User-Group")


generic_meetup("belgian_puppet_user_group", "Belgian-Puppet-User-Group")


generic_meetup("bescala", "BeScala")


@event_source
def bhackspace(create_event):
    soup = BeautifulSoup(urlopen("http://wiki.bhackspace.be/index.php/Main_Page").read())

    if soup.table.find('table', 'table') is None:
        return

    for event in soup.find('table', 'table')('tr')[1:]:
        title = event.a.text
        url = "http://wiki.bhackspace.be" + event.a["href"]
        start = parse(event('td')[1].text)
        location = event('td')[2].text

        create_event(
            title=title,
            url=url,
            start=start,
            location=location.strip() if location else None
        )

generic_meetup("bigdata_be", "bigdatabe")


@event_source
def blender_brussels(create_event):
    soup = BeautifulSoup(urlopen("https://blender-brussels.github.io/"))

    for entry in soup("article", attrs={"class":None}):
        start = entry.find("time")
        title = entry.text
        url = entry.find("a")["href"]
        start = datetime.strptime(entry.find("time")["datetime"][:-6], "%Y-%m-%dT%H:%M:%S")

        create_event(
            title=title,
            url=url,
            start=start
        )


generic_meetup("brussels_cassandra_users", "Brussels-Cassandra-Users")


generic_meetup("brussels_data_science_meetup", "Brussels-Data-Science-Community-Meetup")


generic_meetup("brussels_wordpress", "wp-bru")


@event_source
def budalab(create_event):
    now = int(time.time())
    then = now + (60 * 60 * 24 * 14)
    location = "Designregio Kortrijk, Broelkaai 1B, 8500 KORTRIJK"
    data = json.load(urlopen("http://budalab.fikket.com/api2/events/calendar.json?start=%s&end=%s"%(now, then)))

    for entry in data:
        title = entry["title"]
        start = datetime.strptime(entry["start"][:-6], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(entry["end"][:-6], "%Y-%m-%dT%H:%M:%S")

        create_event(
            title=title,
            location = location,
            url=entry["url"],
            start=start,
            end=end
        )


@event_source
def bxlug(create_event):
    soup = BeautifulSoup(urlopen("http://www.bxlug.be/spip.php?page=agenda-zpip"))
    for entry in soup('article', 'evenement'):
        # [:-1] => ignore timezones, because sqlite doesn't seem to like it
        start = parse(entry('meta', itemprop='startDate')[0]['content'][:-1])
        end = parse(entry('meta', itemprop='endDate')[0]['content'][:-1])
        title = entry('span', itemprop='name')[0].text
        url = "http://www.bxlug.be/" + entry('a', itemprop='url')[0]['href']
        create_event(
            title=title,
            url=url,
            start=start,
            end=end
        )


@event_source
def constantvzw(create_event):
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

        create_event(
            title=title,
            url=url,
            start=start,
            end=end,
            location=location.strip() if location else None
        )


generic_meetup("docker_belgium", "Docker-Belgium")


generic_meetup("ember_js_brussels", "Ember-js-Brussels")


@event_source
def foam(create_event):
    soup = BeautifulSoup(urlopen("http://fo.am/events/").read())

    for line in soup.find('table', 'eventlist')('tr')[1:]:
        title, event_date = line('td')

        link = title.a['href']

        dates = map(parse, event_date.text.split('-'))
        if len(dates) == 2:
            start, end = dates
        else:
            start, end = dates[0], None

        event = create_event(
            title=title.text,
            url='http://fo.am' + link,
            start=start,
            end=end
        )

        if "FoAM Apéro" in event.title:
            event.tags.add("meeting")


@event_source
def hsbxl(create_event):
    today = date.today() - timedelta(days=6 * 30)

    data = json.load(urlopen("https://hackerspace.be/Special:Ask/-5B-5BCategory:TechTue-7C-7CEvent-5D-5D-20-5B-5BEnd-20date::-3E%s-2D%s-2D%s-20-5D-5D/-3FStart-20date/-3FEnd-20date/-3FLocation/format%%3Djson/sort%%3D-5BStart-20date-5D/order%%3Dasc/offset%%3D0'" % (today.year, today.month, today.day)))

    for event in data["results"].values():
        db_event = create_event(
            title=event["fulltext"],
            url=event["fullurl"],
            start=datetime.fromtimestamp(int(event["printouts"]["Start date"][0])),
            end=datetime.fromtimestamp(int(event["printouts"]["End date"][0])),
            location=event["printouts"]["Location"][0]["fulltext"]
        )

        if "TechTue" in event["fulltext"]:
            db_event.tags.add("meeting")


@event_source
def incubhacker(create_event):
    now = calendar.timegm(datetime.now().utctimetuple())

    # 2 magics numbers are from a reverse of the incubhacker calendar api
    for event in json.load(urlopen("http://www.incubhacker.be/index.php/component/gcalendar/jsonfeed?format=raw&gcid=2&start=%s&end=%s" % (now - 1187115, now + 2445265))):
        title = event["title"]
        url = "http://www.incubhacker.be" + event["url"]
        start = parse(event["start"]).replace(tzinfo=None)
        end = parse(event["end"]).replace(tzinfo=None)

        event = create_event(
            title=title,
            url=url,
            start=start,
            end=end
        )

        if event.title.strip() in ("INCUBHACKER", "Réunion normale"):
            event.tags.add("meeting")


generic_meetup("laravel_brussels", "Laravel-Brussels")


generic_meetup("les_mardis_de_l_agile", "Les-mardis-de-lagile-Bruxelles")


generic_meetup("mongodb_belgium", "MongoDB-Belgium")


@event_source
def neutrinet(create_event):
    soup = BeautifulSoup(urlopen("http://neutrinet.be/index.php?title=Main_Page").read())

    if not soup.table.table.tr.find('table', 'wikitable'):
        return

    for event in filter(lambda x: x, map(lambda x: x('td'), soup.table.table.tr.find('table', 'wikitable')('tr'))):
        title = event[0].text
        url = "https://neutrinet.be" + event[0].a["href"]
        start = parse(event[1].text)
        location = event[2].text

        event = create_event(
            title=title,
            url=url,
            start=start,
            location=location.strip() if location else None
        )

        if "Meeting" in event.title:
            event.tags.add("meeting")


@event_source
def okfnbe(create_event):
    data = Calendar.from_ical(urlopen("https://www.google.com/calendar/ical/sv07fu4vrit3l8nb0jlo8v7n80@group.calendar.google.com/public/basic.ics").read())

    for event in data.walk()[1:]:
        if event.get("DTSTAMP"):
            title = str(event["SUMMARY"]) if event.get("SUMMARY") else  ""
            url = (str(event["URL"]) if str(event["URL"]).startswith("http") else "http://" + str(event["URL"])) if event.get("URL") else "http://okfn.be/"
            start = str(event["DTSTART"].dt)  if event.get("DTSTART") else str(event["DTSTAMP"].dt)
            end = str(event["DTEND"].dt) if event.get("DTEND") else None
            location = event["LOCATION"]

            #timezone removal, the crappy way
            if len(start) > 10:
                start = start[:-6]
            if len(end) > 10:
                end = end[:-6]

            event = create_event(
                title=title,
                url=url,
                start=start,
                end=end,
                location=location
            )


@event_source
def okno(create_event):
    soup = BeautifulSoup(urlopen("http://www.okno.be/events/").read())

    for entry in soup('div', 'switch-events'):
        datetuple = map(int, entry('span', 'date-display-single')[0].text.split('.'))
        title = entry('span', 'field-content')[0].text
        link = "http://www.okno.be" + entry('a')[0]['href']
        create_event(
            title=title,
            url=link,
            start=datetime(*datetuple)
        )


generic_meetup("opengarage", "OpenGarage")


generic_meetup("opentechschool", "OpenTechSchool-Brussels")


@event_source
def owaspbe(create_event):
    soup = BeautifulSoup(urlopen("http://www.eventbrite.com/o/owasp-belgium-chapter-1865700117").read())

    for event in soup.findAll("div", attrs= {"class" : "event_row vevent clrfix"}):
        title = event.find("span", attrs = {"class" : "summary"}).string
        location = event.find("span", attrs = {"class" : "street-address microformats_only"}).text
        start = event.find("span", attrs = {"class" : "dtstart microformats_only"}).text
        end = event.find("span", attrs = {"class" : "dtend microformats_only"}).text
        url = event.find("a", attrs = {"class" : "url"})['href']

        create_event(
            title=title,
            start=start,
            end=end,
            url=url,
            location=location
        )


generic_meetup("phpbenelux", "phpbenelux")


@event_source
def relab(create_event):
    data = Calendar.from_ical(urlopen("https://www.google.com/calendar/ical/utmnk71g19dcs2d0f88q3hf528%40group.calendar.google.com/public/basic.ics").read())

    for event in data.walk()[1:]:
        if event.get("DTSTAMP"):
            title = str(event["SUMMARY"]) if event.get("SUMMARY") else  ""
            url = str(event["URL"]) if event.get("URL") else "http://relab.be"
            start = str(event["DTSTART"].dt)  if event.get("DTSTART") else str(event["DTSTAMP"].dt)
            end = str(event["DTEND"].dt) if event.get("DTEND") else None

            location = event["LOCATION"]

            #timezone removal, the crappy way
            if len(start) > 10:
               start = start[:-6]
            if len(end) > 10:
               end = end[:-6]

            event = create_event(
                title=title,
                url=url,
                start=start,
                end=end,
                location=location
            )


generic_meetup("ruby_burgers", "ruby_burgers-rb")


json_api("urlab", "https://urlab.be/hackeragenda.json")


@event_source
def voidwarranties(create_event):
    data = Calendar.from_ical(urlopen("http://voidwarranties.be/index.php/Special:Ask/-5B-5BCategory:Events-5D-5D/-3FHas-20start-20date=start/-3FHas-20end-20date=end/-3FHas-20coordinates=location/format=icalendar/title=VoidWarranties/description=Events-20at-20http:-2F-2Fvoidwarranties.be/limit=500").read())

    for event in data.walk()[1:]:
        title = str(event["SUMMARY"])
        url = event["URL"]
        start = event["DTSTART"].dt if event.get("DTSTART") else event["DTSTAMP"].dt
        end = event["DTEND"].dt if event.get("DTSTART") else None

        create_event(
            title=title,
            url=url,
            start=start,
            end=end
        )


generic_meetup("webrtc", "WebRTC-crossingborders")


@event_source
def whitespace(create_event):
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

        create_event(
            title=title,
            url=url,
            start=start,
            end=end,
            location=location.strip() if location else None
        )


@event_source
def wolfplex(create_event):
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

        create_event(
            title=title,
            url=url,
            start=start,
            location=location
        )
