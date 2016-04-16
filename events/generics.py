# encoding: utf-8

from datetime import datetime
import facepy
import requests
from dateutil.parser import parse
from icalendar import Calendar
from icalendar import Event as icalendarEvent
from BeautifulSoup import BeautifulSoup
from django.conf import settings

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


def json_api(url):
    """
    Generic function to add events from an urls respecting the json api
    """
    data = requests.get(url, verify=False).json()
    for event in data['events']:
        yield {
            'title': event['title'],
            'url': event['url'],
            'start': parse(event['start']).replace(tzinfo=None),
            'end': parse(event['end']).replace(tzinfo=None) if 'end' in event else None,
            'all_day': event['all_day'] if 'all_day' in event else None,
            'location': event['location'] if 'location' in event else None,
        }


def generic_eventbrite(eventbrite_id):
    src_url = "http://www.eventbrite.com/o/{}".format(eventbrite_id)
    soup = BeautifulSoup(requests.get(src_url).content)

    for event in soup.findAll("div", attrs={"class": "event_row vevent clrfix"}):
        title = event.find("span", attrs={"class": "summary"}).string
        location = event.find("span", attrs={"class": "street-address microformats_only"}).text
        start = event.find("span", attrs={"class": "dtstart microformats_only"}).text
        end = event.find("span", attrs={"class": "dtend microformats_only"}).text
        url = event.find("a", attrs={"class": "url"})['href']

        yield {
            'title': title,
            'start': start,
            'end': end,
            'url': url,
            'location': location,
        }


def generic_meetup(meetup_name):
    data = Calendar.from_ical(requests.get("http://www.meetup.com/{}/events/ical/".format(meetup_name)).content)

    for event in data.walk():
        if not isinstance(event, icalendarEvent):
            continue

        if not event.get("URL", "").split("/")[-2].isdigit():
            continue

        title = event.get("SUMMARY", None)
        start = event.get("DTSTART", None)

        if None in (title, start):
            continue

        detail = {
            "title": title.encode("Utf-8"),
            "url": event.get("URL", ""),
            "start": start.dt.replace(tzinfo=None) if isinstance(start.dt, datetime) else start.dt,
            "location": event.get("LOCATION", "").encode("Utf-8"),
        }

        yield detail


# Facebook pages require APP token
def generic_facebook_page(fb_page):
    if not hasattr(settings, "FACEBOOK_APP_ID") or not hasattr(settings, "FACEBOOK_APP_SECRET"):
        print "ERROR: Facebook Page %s disabled, please define FACEBOOK_APP_ID and FACEBOOK_APP_SECRET in your agenda settings file" % fb_page
        return

    graph = facepy.GraphAPI.for_application(settings.FACEBOOK_APP_ID, settings.FACEBOOK_APP_SECRET)

    for page in graph.get('%s/events?since=0' % fb_page, page=True):
        for event in page['data']:
            yield {
                'title': event['name'],
                'url': 'http://www.facebook.com/%s' % event['id'],
                'start': parse(event['start_time']).replace(tzinfo=None),
                'location': event.get('location'),
            }


# Facebook pages require USER token
def generic_facebook_group(fb_group):
    if not hasattr(settings, "FACEBOOK_USER_TOKEN"):
        print "ERROR: Facebook Group %s disabled, please define FACEBOOK_USER_TOKEN in your agenda settings file" % fb_group
        return

    graph = facepy.GraphAPI(settings.FACEBOOK_USER_TOKEN)

    for page in graph.get('%s/events?since=0' % fb_group, page=True):
        for event in page['data']:
            yield {
                'title': event['name'],
                'url': 'http://www.facebook.com/%s' % event['id'],
                'start': parse(event['start_time']).replace(tzinfo=None),
                'location': event.get('location'),
            }


def generic_google_agenda(gurl, per_event_url_function=None):
    data = Calendar.from_ical(requests.get(gurl).content)

    # Each event has a unique google id, but is present multiple times
    known_uids = {}
    last_modifications = {}

    for event in data.walk():
        if not event.get("DTSTAMP"):
            continue

        uid = event.get("UID")
        last_mod = str(event["LAST-MODIFIED"].dt) if "LAST-MODIFIED" in event else "1970-01-01"
        if uid in last_modifications and last_mod <= last_modifications[uid]:
            continue

        title = str(event["SUMMARY"]) if event.get("SUMMARY") else ""
        if per_event_url_function is None:
            url = (str(event["URL"]) if str(event["URL"]).startswith("http") else "http://" + str(event["URL"])) if event.get("URL") else ""
        else:
            url = per_event_url_function(event)
        start = str(event["DTSTART"].dt) if event.get("DTSTART") else str(event["DTSTAMP"].dt)
        end = str(event["DTEND"].dt) if event.get("DTEND") else None
        location = event.get("LOCATION")

        # timezone removal, the crappy way
        if len(start) > 10:
            start = start[:-6]
        if len(end) > 10:
            end = end[:-6]

        #Event modification: update record
        if uid in known_uids:
            ev = known_uids[uid]
            last_modifications[uid] = last_mod
            ev['title'] = title
            ev['url'] = url
            ev['start'] = start
            ev['end'] = end
            ev['location'] = location
        else:
            detail = {
                'title': title,
                'url': url,
                'start': start,
                'end': end,
                'location': location,
            }
            last_modifications[uid] = last_mod
            known_uids[uid] = detail

    return iter(filter(lambda x: not x["url"].startswith("<"), known_uids.values()))
