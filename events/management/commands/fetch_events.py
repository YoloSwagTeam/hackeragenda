# encoding: utf-8

import sys
import requests
import traceback

from datetime import datetime
from collections import OrderedDict

from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse
from icalendar import Calendar
from icalendar import Event as icalendarEvent
from optparse import make_option

import facepy

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event
from django.conf import settings

from imp import load_source
from os import listdir

# instead of doing .encode("Utf-8") everywhere, easier for contributors
reload(sys)
sys.setdefaultencoding("utf-8")

SOURCES_FUNCTIONS = OrderedDict()
SOURCES_OPTIONS = {}

month_convertor = (
    ("Janvier", "January"),
    ("Février", "February"),
    ("Mars", "March"),
    ("Avril", "April"),
    ("Mai", "May"),
    ("Juin", "June"),
    ("Juillet", "July"),
    ("Août", "August"),
    ("Septembre", "September"),
    ("Novembre", "November"),
    ("Décembre", "December"),
)

def french_month_to_english_month(to_convert):
    for i, j in month_convertor:
        to_convert = to_convert.replace(i, j)
    return to_convert


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='No debug output'),
    )

    def handle(self, *args, **options):
        sources = SOURCES_FUNCTIONS.keys() if not args else args

        for source in sources:
            try:
                with transaction.commit_on_success():
                    SOURCES_FUNCTIONS[source](options.get('quiet', True))

            except Exception as e:
                traceback.print_exc(file=sys.stdout)
                print "While working on '%s', got this exception:" % source
                print e


def event_source(background_color, text_color, url, agenda=None, key="url", description=""):
    if agenda is None:
        agenda = CURRENT_AGENDA
    def event_source_wrapper(func, org_name=None):
        def fetch_events(quiet):
            def create_event(**detail):
                if key not in (None, False) and Event.objects.filter(**{key: detail[key]}):
                    Event.objects.filter(**{key: detail[key]}).delete()

                res = Event.objects.create(source=org_name, text_color=SOURCES_OPTIONS[org_name]["fg"], border_color=SOURCES_OPTIONS[org_name]["bg"], agenda=agenda, **detail)
                if not quiet:
                    print unicode(res)
                return res

            if key in (None, False):
                Event.objects.filter(source=org_name).delete()
            else:
                Event.objects.filter(source=org_name, start__gte=datetime.now())
                Event.objects.filter(source=org_name).update(border_color=SOURCES_OPTIONS[org_name]["bg"], text_color=SOURCES_OPTIONS[org_name]["fg"])

            func(create_event)
            if not quiet:
                print " === Finished for " + org_name

        if org_name is None:
            org_name = func.__name__.lower()

        SOURCES_OPTIONS[org_name] = {"bg": background_color, "fg": text_color, "agenda": agenda, "description": func.__doc__ if not description and func.__doc__ else description, "url": url}

        SOURCES_FUNCTIONS[org_name] = fetch_events

        return func

    return event_source_wrapper


def json_api(org_name, url, background_color, text_color, source_url, agenda=None, tags=None, description=""):
    def fetch(create_event):
        """
        Generic function to add events from an urls respecting the json api
        """
        data = requests.get(url, verify=False).json()
        for event in data['events']:
            db_event = create_event(
                title=event['title'],
                url=event['url'],
                start=parse(event['start']).replace(tzinfo=None),
                end=parse(event['end']).replace(tzinfo=None) if 'end' in event else None,
                all_day=event['all_day'] if 'all_day' in event else None,
                location=event['location'] if 'location' in event else None,
            )

            if tags:
                db_event.tags.add(*tags)

    return event_source(background_color, text_color, agenda=agenda, key=None, description=description, url=url)(fetch, org_name)


def generic_eventbrite(org_name, eventbrite_id, background_color, text_color, url, agenda=None, tags=None, description=""):
    def fetch(create_event):
        src_url = "http://www.eventbrite.com/o/{}".format(eventbrite_id)
        soup = BeautifulSoup(requests.get(src_url).content)

        for event in soup.findAll("div", attrs={"class": "event_row vevent clrfix"}):
            title = event.find("span", attrs={"class": "summary"}).string
            location = event.find("span", attrs={"class": "street-address microformats_only"}).text
            start = event.find("span", attrs={"class": "dtstart microformats_only"}).text
            end = event.find("span", attrs={"class": "dtend microformats_only"}).text
            url = event.find("a", attrs={"class": "url"})['href']

            db_event = create_event(
                title=title,
                start=start,
                end=end,
                url=url,
                location=location
            )

            if tags:
                db_event.tags.add(*tags)

    return event_source(background_color, text_color, agenda=agenda, description=description, url=url)(fetch, org_name)


def generic_meetup(org_name, meetup_name, background_color, text_color, agenda=None, tags=None, description=""):
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

            db_event = create_event(
                title=title.encode("Utf-8"),
                url=event.get("URL", ""),
                start=start.dt.replace(tzinfo=None),
                location=event.get("LOCATION", "").encode("Utf-8"),
            )

            if tags:
                db_event.tags.add(*tags)

    return event_source(background_color, text_color, agenda=agenda, description=description, url="https://meetup.com/" + meetup_name)(fetch, org_name)


def generic_facebook(org_name, fb_group, background_color, text_color, agenda=None, tags=None, description=""):
    if not hasattr(settings, "FACEBOOK_APP_ID") or not hasattr(settings, "FACEBOOK_APP_SECRET"):
        print "ERROR: %s disabled, please define FACEBOOK_APP_ID and FACEBOOK_APP_SECRET in your agenda settings file" % org_name
        return

    graph = facepy.GraphAPI.for_application(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)

    def fetch(create_event):
        for page in graph.get('%s/events?since=0' % fb_group, page=True):
            for event in page['data']:
                db_event = create_event(
                            title=event['name'],
                            url='http://www.facebook.com/%s' % event['id'],
                            start=parse(event['start_time']).replace(tzinfo=None),
                            location=event.get('location'),
                        )

                if tags:
                    db_event.tags.add(*tags)

    if not description:
        # Use the FB group description
        group = graph.get(fb_group)
        if 'about' in group:
            description = group['about']
        elif 'description' in group:
            description = group['description']

    return event_source(background_color, text_color, agenda=agenda, description=description, url="https://www.facebook.com/" + fb_group)(fetch, org_name)


def generic_google_agenda(org_name, gurl, tags=[], **options):
    def fetch(create_event):
        data = Calendar.from_ical(requests.get(gurl).content)
        
        # Each event has a unique google id, but is present multiple times
        known_uids = {}

        for event in data.walk():
            if not event.get("DTSTAMP"):
                continue

            uid = event.get("UID")
            last_mod = str(event["LAST-MODIFIED"].dt) if "LAST-MODIFIED" in event else "1970-01-01"
            if uid in known_uids and last_mod <= known_uids[uid].last_mod:
                continue

            title = str(event["SUMMARY"]) if event.get("SUMMARY") else ""
            url = (str(event["URL"]) if str(event["URL"]).startswith("http") else "http://" + str(event["URL"])) if event.get("URL") else options.get("url", "")
            start = str(event["DTSTART"].dt) if event.get("DTSTART") else str(event["DTSTAMP"].dt)
            end = str(event["DTEND"].dt) if event.get("DTEND") else None
            location = event["LOCATION"]

            # timezone removal, the crappy way
            if len(start) > 10:
                start = start[:-6]
            if len(end) > 10:
                end = end[:-6]

            #Event modification: update record
            if uid in known_uids:
                db_event = known_uids[uid]
                db_event.title = title
                db_event.url = url
                db_event.start = start
                db_event.end = end
                db_event.location = location
                db_event.save()
            else:
                db_event = create_event(
                    title=title,
                    url=url,
                    start=start,
                    end=end,
                    location=location
                )

                if tags:
                    db_event.tags.add(*tags)
                known_uids[uid] = db_event

            db_event.last_mod = last_mod
    return event_source(key=None, **options)(fetch, org_name)

CURRENT_AGENDA = None

def load_agenda(name):
    global CURRENT_AGENDA
    CURRENT_AGENDA = name
    try:
        load_source(name, "agendas/" + name + ".py")
    except Exception as err:
        print " === Error %s when loading fetchers for agenda %s" % (err.__name__, name)
        traceback.print_exc()


def load_agendas():
    for f in listdir("agendas"):
        if f == "__init__.py" or f.split(".")[-1] != 'py':
            continue
        load_agenda(f[:-3])


load_agendas()
