# encoding: utf-8

import sys
import calendar
import requests
import feedparser
import time

from datetime import datetime, date, timedelta
from collections import OrderedDict

from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse
from icalendar import Calendar
from icalendar import Event as icalendarEvent
from optparse import make_option
from HTMLParser import HTMLParser
import facepy

from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify
from events.models import Event
from django.conf import settings

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
                import traceback
                traceback.print_exc(file=sys.stdout)
                print "While working on '%s', got this exception:" % source
                print e


def event_source(background_color, text_color, agenda, url, key="url", description=""):
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


def json_api(org_name, url, background_color, text_color, agenda, source_url, tags=None, description=""):
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


def generic_eventbrite(org_name, eventbrite_id, background_color, text_color, agenda, url, tags=None, description=""):
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


def generic_meetup(org_name, meetup_name, background_color, text_color, agenda, tags=None, description=""):
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

def generic_facebook(org_name, fb_group, background_color, text_color, agenda, tags=None, description=""):
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

@event_source(background_color="#133F52", text_color="#FFFFFF", key=None, agenda="be", url="https://groups.google.com/d/forum/afpyro-be")
def afpyro(create_event):
    '<p>Les apéros des amateurs du langage de programmation <a href="https://www.python.org/">python</a>.</p>'
    soup = BeautifulSoup(requests.get("http://afpyro.afpy.org/").content)
    filtering = lambda x: x['href'][:7] == '/dates/' and '(BE)' in x.text
    for link in filter(filtering, soup('a')):
        datetuple = map(int, link['href'].split('/')[-1].split('.')[0].split('_'))
        event = create_event(
            title=link.text,
            start=datetime(*datetuple),
            url="http://afpyro.afpy.org" + link['href']
        )

        event.tags.add("python", "programming", "drink")


@event_source(background_color="#3A87AD", text_color="white", agenda="be", url="http://www.agendadulibre.be")
def agenda_du_libre_be(create_event):
    "<p>L'agenda des évènements du Logiciel Libre en Belgique.</p>"
    data = Calendar.from_ical(requests.get("http://www.agendadulibre.be/ical.php?region=all").content)

    for event in data.walk()[1:]:
        db_event = create_event(
            title=event["SUMMARY"].encode("Utf-8"),
            url=event["URL"],
            start=event["DTSTART"].dt.replace(tzinfo=None),
            location=event["LOCATION"].encode("Utf-8")
        )

        db_event.tags.add(slugify(event["LOCATION"].encode("Utf-8")))
        db_event.tags.add("libre")

# @event_source(background_color="#3A87AD", text_color="white", agenda="fr")
# def agenda_du_libre_fr(create_event):
#     data = Calendar.from_ical(urlopen("http://www.agendadulibre.org/ical.php?region=all"))
#
#     for event in data.walk()[1:]:
#         create_event(
#             title=event["SUMMARY"].encode("Utf-8"),
#             url=event["URL"],
#             start=event["DTSTART"].dt.replace(tzinfo=None),
#             location=event["LOCATION"].encode("Utf-8")
#         )


generic_meetup("agile_belgium", "Agile-Belgium", background_color="#D2353A", text_color="white", agenda="be", description="<p>This is the meetup group of the Agile Belgium community. We organize regular drinkups and user group meetings. Come after work and meet people you usually only meet at conferences. Anyone interested in Agile or Lean can join.</p>")


@event_source(background_color="#005184", text_color="white", agenda="fr", url="https//www.april.org")
def april(create_event):
    '<p>Pionnière du <strong><a href="http://www.april.org/articles/intro/ll.html" title="Lien vers la page Qu\'est-ce qu\'un logiciel libre ?">logiciel libre</a></strong> en France, l\'April, constituée de 4063 adhérents (3676 individus, 387 entreprises, associations et organisations), est depuis 1996 un acteur majeur de la <strong>démocratisation</strong> et de la <strong>diffusion</strong> du logiciel libre et des <strong>standards ouverts</strong> auprès du grand public, des professionnels et des institutions dans l\'espace francophone. <a href="http://www.april.org/fr/association/" title="En savoir plus sur l\'April">En savoir plus...</a>.</p>'
    data = feedparser.parse("https://www.april.org/fr/event/feed")

    for event in data.entries:
        soup = BeautifulSoup(event["summary"])
        start, end = map(lambda x: datetime.strptime(french_month_to_english_month(x.contents[-1]), "%d %B %Y - %H:%M"), soup("div", "event-start"))
        url = event["link"]
        title = event["title"]

        db_event = create_event(
            title=title,
            url=url,
            start=start,
            end=end,
        )

        db_event.tags.add("libre")


generic_meetup("aws_user_group_belgium", "AWS-User-Group-Belgium", background_color="#F8981D", text_color="white", agenda="be", tags=["cloud", "amazon", "aws", "sysadmin"], description="<p>This is a group for anyone interested in cloud computing on the Amazon Web Services platform. All skills levels are welcome.</p>")


generic_meetup("belgian_angularjs", "The-Belgian-AngularJS-Meetup-Group", background_color="#9D3532", text_color="white", agenda="be", tags=["angularjs", "javascript", "webdev", "programming"], description="<p>Let's get together for some discussions about the awesome AngularJS framework! I started this group to meet the belgian AngularJS community and share together our experience.</p>")


generic_meetup("belgian_nodejs_user_group", "Belgian-node-js-User-Group", background_color="#1D1D1D", text_color="white", agenda="be", tags=["nodejs", "javascript", "programming"], description='<p>This node.js user group gathers the belgian node.js developers so we can improve our skill set and build kick-ass amazing apps.<br><br>For the time being: find us on line at <a href="http://www.shadowmedia.be/nodejs/">http://www.shadowmedia.be/nodejs/</a>.</p>')


generic_meetup("belgian_puppet_user_group", "Belgian-Puppet-User-Group", background_color="#7B6DB0", text_color="white", agenda="be", tags=["puppet", "sysadmin", "devops"], description="<p>Bringing puppet loving people together on a regular base, to talk about best practices, their experience and have interesting discussions about a great configuration management tool.<br><br>IRC: freenode - #puppet-be</p>")


generic_meetup("bescala", "BeScala", background_color="#FEE63C", text_color="#000000", agenda="be", tags=["java", "scala", "jvm", "programming"], description="<p>The Belgian Scala User Group.</p>")


generic_facebook("bite_back", "BiteBackOrg", background_color="#db0c38", text_color="#FFFFFF", agenda="vg_be", tags=["animal-rights"])


@event_source(background_color="DarkGoldenRod", text_color="white", agenda="be", url="http://bhackspace.be")
def bhackspace(create_event):
    "<p>The BHackspace is a hackerspace located in Bastogne, Belgium.</p>"
    soup = BeautifulSoup(requests.get("http://wiki.bhackspace.be/index.php/Main_Page").content)

    if soup.table.find('table', 'table') is None:
        return

    for event in soup.find('table', 'table')('tr')[1:]:
        title = event.a.text
        url = "http://wiki.bhackspace.be" + event.a["href"]
        start = parse(event('td')[1].text)
        location = event('td')[2].text

        db_event = create_event(
            title=title,
            url=url,
            start=start,
            location=location.strip() if location else "Bastogne"
        )

        db_event.tags.add("hackerspace", "bastogne")


generic_meetup("bigdata_be", "bigdatabe", background_color="black", text_color="white", agenda="be", tags=["bigdata", "programming", "nosql"], description="<p>Welcome to our Belgian community about bigdata, NoSQL and anything data. If you live or work in Belgium and are interested in any of these technologies, please join! We want you!</p>")


@event_source(background_color="#828282", text_color="white", key=None, agenda="be", url="https://blender-brussels.github.io/")
def blender_brussels(create_event):
    '<p>The <strong>Blender-Brussels</strong> − also known as <strong>Blender BPY/BGE workshops</strong> − are a series of monthly work sessions organized by <a href="http://xuv.be">Julien Deswaef</a> (<a href="https://github.com/xuv" class="user-mention">@xuv</a>) and <a href="http://frankiezafe.org">François Zajéga</a> (<a href="https://github.com/frankiezafe" class="user-mention">@frankiezafe</a>) with the aim of providing a regular gathering and knowledge sharing space for artists and coders interested in Python scripting in the context of Blender.</p>'

    soup = BeautifulSoup(requests.get("https://blender-brussels.github.io/").content)

    for entry in soup("article", attrs={"class": None}):
        start = entry.find("time")
        title = entry.text
        url = entry.find("a")["href"]
        start = datetime.strptime(entry.find("time")["datetime"][:-6], "%Y-%m-%dT%H:%M:%S")

        db_event = create_event(
            title=title,
            url="https:" + url,
            start=start
        )

        db_event.tags.add("bruxelles", "blender", "3D-modeling")


generic_meetup("brussels_cassandra_users", "Brussels-Cassandra-Users", background_color="#415A6C", text_color="#CBE5F7", agenda="be", tags=["nosql", "jvm", "database", "bruxelles", "programming"], description="<p>Open to all those interested in Apache Cassandra, Big Data, Hadoop, Hive, Hector, NoSQL, Pig, and high scalability. Let's get together and share what we know!</p>")


generic_meetup("brussels_data_science_meetup", "Brussels-Data-Science-Community-Meetup", background_color="#CAD9EC", text_color="black", agenda="be", tags=["bruxelles", "programming", "bigdata"], description='<p>The <strong>Blender-Brussels</strong> − also known as <strong>Blender BPY/BGE workshops</strong> − are a series of monthly work sessions organized by <a href="http://xuv.be">Julien Deswaef</a> (<a href="https://github.com/xuv" class="user-mention">@xuv</a>) and <a href="http://frankiezafe.org">François Zajéga</a> (<a href="https://github.com/frankiezafe" class="user-mention">@frankiezafe</a>) with the aim of providing a regular gathering and knowledge sharing space for artists and coders interested in Python scripting in the context of Blender.</p>')


generic_meetup("brussels_wordpress", "wp-bru", background_color="#0324C1", text_color="white", agenda="be", tags=["bruxelles", "wordpress", "cms", "php", "webdev"], description='<p>A gathering of WordPress users and professionals of all levels.<br><br>Whether you\'re a site owner, designer, developer, plug-in creator all are welcome to attend to learn, share and expand their knowledge of WordPress.<br><br>Have a look at <a href="http://www.meetup.com/wp-bru/about/">our about page</a> for a idea of the type of activities I\'d like to see organised.</p>')


@event_source(background_color="#FEED01", text_color="black", agenda="be", url="http://budalab.fikket.com")
def budalab(create_event):
    """
    <p>
    BUDA::lab is een meetingspot, een open werk- plek voor designers,
    studenten, bedrijven, kunstenaars, actieve DIY'ers, ... BUDA::lab is een
    plek om te creeren, om te materialiseren, om ervaring te delen, kennis te
    verzamelen en uitgedaagd te worden. Sluit je aan, loop binnen wanneer je
    wil en ontdek wat BUDA::lab voor jou kan betekenen!
    </p>
    """
    now = int(time.time())
    then = now + (60 * 60 * 24 * 14)
    location = "Designregio Kortrijk, Broelkaai 1B, 8500 KORTRIJK"
    data = requests.get("http://budalab.fikket.com/api2/events/calendar.json?start=%s&end=%s"%(now, then)).json()

    for entry in data:
        title = entry["title"]
        start = datetime.strptime(entry["start"][:-6], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(entry["end"][:-6], "%Y-%m-%dT%H:%M:%S")

        db_event = create_event(
            title=title,
            location=location,
            url=entry["url"],
            start=start,
            end=end
        )

        db_event.tags.add("fablab")


@event_source(background_color="white", text_color="#990000", agenda="be", url="http://www.bxlug.be")
def bxlug(create_event):
    """
    <p>Le BxLUG est une association d’utilisateurs de logiciels libres créée en 1999 et dont l’objectif est la promotion de GNU/Linux et autres logiciels libres dans la région de Bruxelles.</p>

    <p>Nous proposons régulièrement des activités conviviales&nbsp;:<br><img src="squelettes-dist/puce.gif" class="puce" alt="-" height="11" width="8">&nbsp;<a href="spip.php?article13" class="spip_in">Linux Copy Party</a><br><img src="squelettes-dist/puce.gif" class="puce" alt="-" height="11" width="8">&nbsp;<a href="spip.php?article10" class="spip_in">Atelier Info Linux</a></p>

    <p>Nous proposons également <a href="spip.php?rubrique8" class="spip_in">des listes de discussion ouvertes</a>  pour l’entraide quotidienne.</p>

    <p><a href="spip.php?rubrique4" class="spip_out">Nos rencontres aident tout un chacun à installer et configurer des systèmes libres, à approfondir leurs connaissances et à découvrir de nouveaux horizons</a></p>

    <p>Le BxLUG est partenaire bénévole avec<br><img src="squelettes-dist/puce.gif" class="puce" alt="-" height="11" width="8">&nbsp;<a href="http://www.lefourquet.be/Accueil_-_A_la_Une.html" class="spip_out" rel="external">Le Fourquet</a><br><img src="squelettes-dist/puce.gif" class="puce" alt="-" height="11" width="8">&nbsp;<a href="http://www.fij.be/" class="spip_out" rel="external">Formation Insertion Jeune FIJ</a><br><img src="squelettes-dist/puce.gif" class="puce" alt="-" height="11" width="8">&nbsp;<a href="http://www.bxlug.be/spip.php?article10&amp;id_evenement=121" class="spip_out">Info Linux, Atelier du Web</a></p>
    """
    soup = BeautifulSoup(requests.get("http://www.bxlug.be/spip.php?page=agenda-zpip").content)
    for entry in soup('article', 'evenement'):
        # [:-1] => ignore timezones, because sqlite doesn't seem to like it
        start = parse(entry('meta', itemprop='startDate')[0]['content'][:-1])
        end = parse(entry('meta', itemprop='endDate')[0]['content'][:-1])
        title = entry('span', itemprop='name')[0].text
        url = "http://www.bxlug.be/" + entry('a', itemprop='url')[0]['href']
        db_event = create_event(
            title=title,
            url=url,
            start=start,
            end=end
        )

        db_event.tags.add("lug", "bruxelles", "libre")


@event_source(background_color="#D2C7BA", text_color="black", key=None, agenda="be", url="http://www.constantvzw.org")
def constantvzw(create_event):
    """
    <p><strong>Constant is a non-profit association, an interdisciplinary arts-lab based and active in Brussels since 1997.</strong></p>

    <p>Constant works in-between media and art and is interested in the culture and ethics of the World Wide Web. The artistic practice of Constant is inspired by the way that technological infrastructures, data-exchange and software determine our daily life. Free software, copyright alternatives and (cyber)feminism are important threads running through the activities of Constant.</p>

    <p>Constant organizes workshops, print-parties, walks and ‘Verbindingen/Jonctions’-meetings on a regular basis for a public that’s into experiments, discussions and all kinds of exchanges.</p>
    """
    soup = BeautifulSoup(requests.get("http://www.constantvzw.org/site/").content)

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

        db_event = create_event(
            title=title,
            url=url,
            start=start,
            end=end,
            location=location.strip() if location else None
        )

        db_event.tags.add("artist", "libre")


generic_meetup("docker_belgium", "Docker-Belgium", background_color="#008FC4", text_color="white", agenda="be", tags=["docker", "lxc", "sysadmin", "devops"], description='<p>Meet other developers and ops engineers using Docker.&nbsp;Docker is an open platform for developers and sysadmins to build, ship, and run distributed applications. Consisting of Docker Engine, a portable, lightweight runtime and packaging tool, and Docker Hub, a cloud service for sharing applications and automating workflows, Docker enables apps to be quickly assembled from components and eliminates the friction between development, QA, and production environments. As a result, IT can ship faster and run the same app, unchanged, on laptops, data center VMs, and any cloud.</p><p>Learn more about Docker at&nbsp;<a href="http://www.docker.com/">http://www.docker.com</a></p>')


@event_source(background_color="#2C2C29", text_color="#89DD00", agenda="fr", url="http://www.electrolab.fr")
def electrolab(create_event):
    '<p><a title="Electrolab" href="../" target="_blank">L’Electrolab</a> est un hacker space dans la zone industrielle de Nanterre. À quelques stations de RER du centre de Paris, Ce nouveau Fablab de la région parisienne est, comme son nom l’indique, dédié aux projets ayant une forte connotation électronique et / ou mécanique.</p>'

    data = Calendar.from_ical(requests.get("http://www.electrolab.fr/?plugin=all-in-one-event-calendar&controller=ai1ec_exporter_controller&action=export_events&cb=493067527").content)

    for event in data.walk()[4:]:
        title = str(event["SUMMARY"])
        location = str(event["LOCATION"])
        url = event["URL"]
        start = datetime.combine(event["DTSTART"].dt, datetime.min.time()).replace(tzinfo=None)
        end = datetime.combine(event["DTEND"].dt, datetime.min.time()).replace(tzinfo=None) if event.get("DTEND") else None

        db_event = create_event(
            title=title,
            location=location,
            url=url,
            start=start,
            end=end,
        )

        db_event.tags.add("hackerspace")


generic_meetup("ember_js_brussels", "Ember-js-Brussels", background_color="#FC745D", text_color="white", agenda="be", tags=["emberjs", "javascript", "programming", "webdev"], description="This is a group for anyone interested in developing web applications in Ember.js. I created this group because it's nice to have a local community for sharing knowledge, ideas and inspiration about this awesome web framework. The learning curve for Ember.js is not the lightest so it will also be a place to share your frustrations! Beginner or expert, everyone is welcome.")


@event_source(background_color="#539316", text_color="#FFFFFF", agenda="vg_be", url="http://www.evavzw.be")
def eva(create_event):
    """EVA werd opgericht in 2000 door een handjevol gemotiveerde mensen uit het Gentse en is sindsdien uitgegroeid tot een organisatie met een tiental vaste medewerkers, verschillende lokale groepen en honderden vrijwilligers. Sinds haar ontstaan heeft de organisatie al heel wat activiteiten en projecten op poten gezet."""
    nl_months = {
             'januari': 1,
             'februari': 2,
             'maart': 3,
             'april': 4,
             'mei': 5,
             'juni': 6,
             'juli': 7,
             'augustus': 8,
             'september': 9,
             'oktober': 10,
             'november': 11,
             'december': 12
             }

    tags_mapping = {
            'EVA kookcursus': 'cooking class',
            'kookcursus': 'cooking class',
            'eten': 'eating',
            'EVA eten': 'eating',
            }

    now = datetime.now()

    src_url = "http://www.evavzw.be/index.php?option=com_agenda"
    soup = BeautifulSoup(requests.get(src_url).content)
    for month in soup(attrs={"class":'agenda'}):
        month_nb = int(nl_months[month['id'].split('_')[1]])

        # If the month has passed assume it's next year
        if month_nb < now.month:
            year = now.year + 1
        else:
            year = now.year

        for day in month('li'):
            if day.get('id') is None:
                continue

            day_nb = int(day['id'].split('_')[1])
            for event in day('li'):
                title = event.a.text
                url = 'http://www.evavzw.be/' + event.a['href']
                hour, minute = 0, 0
                tags = []

                for span in event('span'):
                    if 'time' in span['class']:
                        hour, minute = map(int, span.text.split('vanaf ')[1].split('u'))
                    else:
                        # Tag
                        tag = tags_mapping.get(span.text)
                        if tag is not None:
                            tags.append(tag)

                start = datetime(year, month_nb, day_nb, hour, minute)

                event = create_event(
                    title=title,
                    url=url,
                    start=start,
                )

                for tag in tags:
                    event.tags.add(tag)


@event_source(background_color="#C9C4BF", text_color="black", key=None, agenda="be", url="http://fo.am")
def foam(create_event):
    """
    <p>
    FoAM is a network of transdisciplinary labs for speculative culture. It is
    inhabited by people with diverse skills and interests – from arts, science,
    technology, entrepreneurship, cooking, design and gardening. It is a
    generalists’ community of practice working at the interstices of
    contrasting disciplines and worldviews.&nbsp;Guided by our motto “grow your
    own worlds,” we study and prototype possible futures, while remaining
    firmly rooted in cultural traditions. We speculate about the future by
    modelling it in artistic experiments that allow alternative perspectives to
    emerge. By conducting these experiments in the public sphere, we invite
    conversations and participation of people from diverse walks of life.
    </p>
    """

    soup = BeautifulSoup(requests.get("http://fo.am/events/").content)

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


generic_facebook("gaia", "gaia.be", background_color="#fdfafa", text_color="#5d3b80", agenda="vg_be", tags=["animal-rights"])


@event_source(background_color="coral", text_color="white", key=None, agenda="be", url="https://hackerspace.be")
def hsbxl(create_event):
    '''
    <p>
    Hacker Space Brussels (HSBXL) is a space, dedicated to various aspects
    of constructive &amp; creative <a href="/Hacking"
    title="Hacking">hacking</a>, <a href="/Location" title="Location"
    class="mw-redirect"> located</a> in St-Josse. The space is about 300 square
    meters, there is a little electronics lab with over 9000 components, a
    library,and lots of tools. You\'re always welcome to follow one of the
    workshops or come to the weekly <a href="/TechTueList" title="TechTueList">
    Tuesday meetings</a>, hack nights or other get-together events.
    </p>
    '''

    today = date.today() - timedelta(days=6 * 30)

    data = requests.get("https://hackerspace.be/Special:Ask/-5B-5BCategory:TechTue-7C-7CEvent-5D-5D-20-5B-5BEnd-20date::-3E%s-2D%s-2D%s-20-5D-5D/-3FStart-20date/-3FEnd-20date/-3FLocation/format%%3Djson/sort%%3D-5BStart-20date-5D/order%%3Dasc/offset%%3D0'" % (today.year, today.month, today.day), verify=False).json()

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

        db_event.tags.add("hackerspace")


@event_source(background_color="#296038", text_color="#6FCE91", agenda="be", url="http://www.incubhacker.be")
def incubhacker(create_event):
    "<p>Incubhacker est un hackerspace basé dans la région namuroise, c'est un espace de rencontre et de création interdisciplinaire.</p>"

    now = calendar.timegm(datetime.now().utctimetuple())

    # 2 magics numbers are from a reverse of the incubhacker calendar api
    for event in requests.get("http://www.incubhacker.be/index.php/component/gcalendar/jsonfeed?format=raw&gcid=2&start=%s&end=%s" % (now - 1187115, now + 2445265)).json():
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

        event.tags.add("hackerspace")


@event_source(background_color="#66b822", text_color="#FFFFFF", agenda="vg_be", url="http://www.jeudiveggie.be")
def jeudi_veggie(create_event):
    """Le Jeudi Veggie est une campagne qui nous invite à découvrir un jour par semaine, une assiette plus équilibrée, qui fait la part belle aux céréales, aux fruits et aux légumes. Une assiette sans viande ni poisson, mais avec plein de fruits et légumes."""
    tags_mapping = {
            'atelier': 'cooking class',
            'cours de cuisine': 'cooking class',
            'diner': 'eating',
            }

    # request events from today to next year
    today = datetime.now().strftime("%d-%m-%Y")
    next_year = (datetime.now() + timedelta(weeks=52)).strftime("%d-%m-%Y")

    src_url = "http://www.jeudiveggie.be/kalender/zoeken/%s_%s/" % (today, next_year)
    soup = BeautifulSoup(requests.get(src_url).content)

    main = soup.find(id='itemtag')
    for d in main(attrs={'class': 'date'}):
        full_date = d['href'].split('/')[2]
        day, month, year = full_date.split('-')

        url = 'http://www.jeudiveggie.be' + d['href']
        if d.text[2] == ':':
            time, title = d.text.split(' ', 1)
            hour, minute = time.split(':')

            start = datetime(int(year), int(month), int(day), int(hour), int(minute))
        else:
            title = d.text
            start = datetime(int(year), int(month), int(day))

        event = create_event(
            title=title,
            url=url,
            start=start,
        )

        # tags
        span = d.findNextSibling()
        if span.name == 'span':
            splitted = map(unicode.strip, span.text[1:-1].split(','))

            # first element is a tag
            t = tags_mapping.get(splitted[0])
            if t is not None:
                event.tags.add(t)

            # second one is a location
            if len(splitted) > 1:
                event.location = splitted[1]
                event.save()


generic_meetup("laravel_brussels", "Laravel-Brussels", background_color="#FFFFFF", text_color="#FB503B", agenda="be", tags=["bruxelles", "laravel", "php", "webdev", "programming"], description='<p>A group for anyone interested in learning about and sharing knowledge on Laravel, the "PHP framework for web artisans". The group welcomes beginners and experts, amateurs and pros, young and old, etc. Laravel is an accessible, yet powerful framework for web application development. Its expressive, elegant syntax and its clean structure make PHP development a real joy. As the Laravel community keeps growing, this group is an attempt to get Belgium-based users to know each other, and to spread the word!</p>')


generic_meetup("les_mardis_de_l_agile", "Les-mardis-de-lagile-Bruxelles", background_color="#37C2F1", text_color="black", agenda="be", tags=["bruxelles", "agile", "programming", "drink"], description="<p>Appel à la communauté agile de Bruxelles ! Que vous soyez un fervent agiliste ou tout simplement intéressé par l'agilité, venez découvrir de nouvelles approches, vous enrichir à travers les nombreuses sessions proposées, participer à des innovation games et partager vos retours d'expérience lors de nos meetups \"Les Mardis de l'agile\" !</p>")


generic_meetup("mongodb_belgium", "MongoDB-Belgium", background_color="#3EA86F", text_color="white", agenda="be", tags=["mongodb", "database", "programming"], description="<p>The first countrywide MongoDB user group in Belgium. Meetups will be held every 3 months. Talk proposals can be sent to hannes@showpad.com.</p>")


@event_source(background_color="DarkBlue", text_color="white", agenda="be", url="http://neutrinet.be")
def neutrinet(create_event):
    '''
    <p>Neutrinet is a project dedicated to build associative Internet Service Provider(s) in Belgium.
    </p><p>We want to preserve the Internet as it was designed to be&nbsp;: a decentralized system of interconnected computer networks. We want to bring users back into the network by empowering them, from a technical and knowledge perspective. Neutrinet does not have customers, we have members that contribute to the project as much as they want and/or are able to.
    </p><p>Human rights, Net neutrality, privacy, transparency are our core values.
    </p>
    '''

    soup = BeautifulSoup(requests.get("http://neutrinet.be/index.php?title=Main_Page").content)

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

        event.tags.add("network", "isp")


@event_source(background_color="#299C8F", text_color="white", key=None, agenda="be", url="https://www.google.com")
def okfnbe(create_event):
    """
    <p>Open Knowledge Belgium is a not for profit organisation (vzw/asbl) ran
    by a board of 6 people and has currently 1 employee. It is an umbrella
    organisation for Open Knowledge in Belgium and, as mentioned below, contains
    different working groups of people working around various projects.</p>

    <p>If you would like to have your activities under our wing, please contact us at our mailinglist.</p>
    """

    data = Calendar.from_ical(requests.get("https://www.google.com/calendar/ical/sv07fu4vrit3l8nb0jlo8v7n80@group.calendar.google.com/public/basic.ics").content)

    for event in data.walk()[1:]:
        if not event.get("DTSTAMP"):
            continue

        title = str(event["SUMMARY"]) if event.get("SUMMARY") else ""
        url = (str(event["URL"]) if str(event["URL"]).startswith("http") else "http://" + str(event["URL"])) if event.get("URL") else "http://okfn.be/"
        start = str(event["DTSTART"].dt) if event.get("DTSTART") else str(event["DTSTAMP"].dt)
        end = str(event["DTEND"].dt) if event.get("DTEND") else None
        location = event["LOCATION"]

        # timezone removal, the crappy way
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

        event.tags.add("opendata")


@event_source(background_color="#FFFFFF", text_color="#00AA00", agenda="be", url="http://www.okno.be")
def okno(create_event):
    """
    <p>OKNO is an artist-run organisation connecting new media and ecology. It
    approaches art and culture from a collaborative, DIY and post-disciplinary
    point of view, discovering new materials and aesthetics along the way. The
    OpenGreens rooftop garden and the online server are used as research
    environments during a continuous programme of residencies, workshops, meetings,
    exhibitions and performances.</p>

    <p>For the last few years, OKNO has been focusing on long-term projects,
    involving a diverse and international set of artists and experts sharing an
    interest in the environmental and experimental. Time Inventors’ Kabinet [TIK],
    which revolved around the attempt to devise an ecological time standard, was
    closed in 2012. In 2013, OKNO started on ALOTOF [A Laboratory On The Open
    Fields], a collaborative exploration into the potential of open-air modes of
    creation.</p>
    """
    soup = BeautifulSoup(requests.get("http://www.okno.be/events/").content)

    for entry in soup('div', 'switch-events'):
        datetuple = map(int, entry('span', 'date-display-single')[0].text.split('.'))
        title = entry('span', 'field-content')[0].text
        link = "http://www.okno.be" + entry('a')[0]['href']
        db_event = create_event(
            title=title,
            url=link,
            start=datetime(*datetuple)
        )

        db_event.tags.add("artist")


generic_meetup("opengarage", "OpenGarage", background_color="DarkOrchid", text_color="white", agenda="be", tags=["hackerspace"], description='''<p>The "Open Garage" is a double garage in Borsbeek, Belgium, some sort of <a href="http://en.wikipedia.org/wiki/Hackerspace">hackerspace</a>, where I (<a href="https://plus.google.com/u/2/+AnthonyLiekens/posts">Anthony Liekens</a>) host weekly workshops and many of my projects. The garage is open every Thursday evening to everyone who wants to join our community\'s numerous hacking projects.</p>
<p>Don\'t listen to me, but check out the media\'s reviews of the Open Garage:</p>
<ul>
<li><a href="http://hackaday.com/2013/10/22/hackerspacing-in-europe-garage-space-in-antwerp/">Hackaday\'s review of the Open Garage</a></li>
<li><a href="http://anthony.liekens.net/pub/gva20140614.pdf">The Open Garage in GvA\'s Citta</a> (Belgian newspaper)</li>
<li><a href="https://www.youtube.com/watch?v=aCuUv5ltw6g">The Open Garage in "Iedereen Beroemd"</a> (Belgian national TV)</li>
<li><a href="http://www.radio1.be/programmas/de-bende-van-einstein/binnenkijken-de-garage-van-anthony-liekens">The Open Garage on Radio 1</a> (Belgian national radio)</li>
<li><a href="http://krant.tijd.be/ipaper/20140215#paper/sabato_nl/50">The Open Garage in De Tijd</a> (Belgian "Times" newspaper)</li>
</ul>''')


generic_meetup("opentechschool", "OpenTechSchool-Brussels", background_color="#3987CB", text_color="white", agenda="be", tags=["learning", "programming", "bruxelles"], description='''
<p>OpenTechSchool is a community initiative offering free programming workshops
and meetups to technology enthusiasts of all genders, backgrounds, and
experience levels. It supports volunteer coaches in setting up events by taking
care of the organizational details, encouraging coaches to create original
teaching material.</p>
<p>Everyone is invited to participate, whether as a coach or a learner in this
friendly learning environment where no one feels shy about asking any
questions.</p>
<p><a href="http://www.opentechschool.org/" class="linkified">http://www.opentechschool.org/</a></p>''')


generic_eventbrite("owaspbe", "owasp-belgium-chapter-1865700117", background_color="#4366AF", text_color="white", agenda="be", tags=["security"], description='''
<p>
The Open Web Application Security Project (OWASP) is a <a rel="nofollow"
class="external text"
href="http://www.irs.gov/charities/charitable/article/0,,id=96099,00.html">501(c)(3)</a>
worldwide not-for-profit charitable organization focused on improving the
security of software. Our mission is to make software security <a
rel="nofollow" class="external text"
href="https://www.owasp.org/index.php/Category:OWASP_Video">visible,</a> so
that <a rel="nofollow" class="external text"
href="https://www.owasp.org/index.php/Industry:Citations">individuals and
organizations</a> worldwide can make informed decisions about true software
security risks.
</p>
<p></p>
''', url="https://www.owasp.org/index.php/Belgium")


@event_source(background_color="white", text_color="#B92037", key=None, agenda="fr", url="http://www.pingbase.net")
def ping(create_event):
    """
    <p>
    PiNG explore les pratiques numériques et invite à
    la&nbsp;réappropriation des technologies. A la fois espace de&nbsp;ressources,
    d’expérimentation et atelier de fabrication&nbsp;numérique (Fablab),
    l’association développe son projet&nbsp;autour de la médiation, la pédagogie,
    l’accompagnement&nbsp;et la mise en réseau des acteurs.
    </p>
    <p>
    De l’innovation numérique à l’innovation sociale, PiNG&nbsp;cultive le
    croisement des publics tout en défendant les&nbsp;valeurs de la culture
    libre.
    </p>
    <p>
    Parce que les technologies évoluent vite, mais plus&nbsp;encore les
    pratiques des utilisateurs, PiNG développe&nbsp;des projets et des espaces où
    il est possible&nbsp;d’expérimenter de nouveaux modes de faire,
    des&nbsp;pratiques collectives, des contextes d’apprentissage&nbsp;alternatifs…
    une sorte de «&nbsp;laboratoire citoyen&nbsp;» ouvert&nbsp;et partagé
    s’adressant aussi bien aux acteurs associatifs&nbsp;qu’aux acteurs publics, à
    la communauté créative des&nbsp;artistes, designers, bricoleurs du XXIème
    siècle, au&nbsp;monde de l’éducation et de la recherche.
    </p>
    <p>
    <em>PiNG dispose de l’agrément Jeunesse et Education Populaire.&nbsp;</em>
    </p>
    """

    now = calendar.timegm(datetime.now().utctimetuple())

    # 2 magics numbers are from a reverse of the incubhacker calendar api
    for event in requests.post("http://www.pingbase.net/wp-admin/admin-ajax.php",
                               data={"action": "get_events",
                                     "readonly": True,
                                     "categories": 0,
                                     "excluded": 0,
                                     "start": now - 1187115,
                                     "end": now + 2445265}).json():

        event_data = requests.post("http://www.pingbase.net/wp-admin/admin-ajax.php", data={"action": "get_event", "id": event["id"]}).json()

        event_horrible_inline_content = BeautifulSoup(event_data["content"])

        url = event_horrible_inline_content('a')[-1]["href"] if event_horrible_inline_content.a else "http://www.pingbase.net"

        in_db_event = create_event(
            title=event["title"],
            url=url,
            start=parse(event["start"]),
            end=parse(event["end"]),
        )

        if "aec-repeating" in event["className"]:
            in_db_event.tags.add("meeting")


generic_meetup("phpbenelux", "phpbenelux", background_color="#015074", text_color="white", agenda="be", tags=["php", "programming", "webdev"], description="<p>PHPBenelux user group meetings are a fun way to learn about best practices and new innovations from the world of PHP and to hang out with other PHP developers</p>")

generic_eventbrite("realize", "realize-6130306851", background_color="#36c0cb", text_color="black", agenda="be", tags=["makerspace", "bruxelles"], description="""
<p><strong>Realize</strong> est un atelier partagé<a title="plan" href="https://www.google.be/maps/preview#!q=Rue+du+M%C3%A9tal+32%2C+Saint-Gilles&amp;data=!4m10!1m9!4m8!1m3!1d23940!2d4.802835!3d50.988438!3m2!1i1920!2i912!4f13.1" target="_blank"> situé à Saint-Gilles</a>, à deux pas du Parvis. Tous ceux qui veulent réaliser des objets peuvent y accéder grâce à diverses <a href="http://realizebxl.be/inscription/">formules d’abonnement</a>.</p>
""", url="http://realizebxl.be/")

@event_source(background_color="#2BC884", text_color="white", key=None, agenda="be", url="https://www.google.com")
def relab(create_event):
    """
    <p><strong>Le RElab, premier Fab Lab de Wallonie, est un atelier numérique ouvert au public et une structure de développement créatif local.</strong> La spécificité du RElab réside dans l’utilisation de matériaux de récupération comme matière première et dans l’étude de nouveaux procédés sociaux, créatifs et économiques d’upcycling, en liaison avec les nouveaux moyens&nbsp;de fabrication et de communication numérique.</p>
    """
    data = Calendar.from_ical(requests.get("https://www.google.com/calendar/ical/utmnk71g19dcs2d0f88q3hf528%40group.calendar.google.com/public/basic.ics").content)

    for event in data.walk()[1:]:
        if event.get("DTSTAMP"):
            title = str(event["SUMMARY"]) if event.get("SUMMARY") else ""
            url = str(event["URL"]) if event.get("URL") else "http://relab.be"
            start = str(event["DTSTART"].dt) if event.get("DTSTART") else str(event["DTSTAMP"].dt)
            end = str(event["DTEND"].dt) if event.get("DTEND") else None

            location = event["LOCATION"]

            # timezone removal, the crappy way
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

            event.tags.add("fablab")


generic_meetup("ruby_burgers", "ruby_burgers-rb", background_color="white", text_color="#6F371F", agenda="be", tags=["ruby", "programming", "drink"], description="<p>Ruby lovers meet burger lovers. Join us to talk about ruby AND burgers in the best burger places in Brussels</p>")


json_api("urlab", "https://urlab.be/hackeragenda.json", background_color="pink", text_color="black", agenda="be", tags=["hackerspace"], description="""
<p>
UrLab est le hackerspace de l’ULB. Il s’agit d'un laboratoire ouvert par et
pour les étudiants, où l’on met à disposition une infrastructure pour qu’ils
puissent y exprimer leur créativité de manière collaborative.
</p>
""", source_url="http://urlab.be")


@event_source(background_color="#82FEA9", text_color="#DC0000", agenda="be", url="https://www.hackerspace.lu/")
def syn2cat(create_event):
    "<p>L'agenda du Syn2Cat, hackerspace Luxembourgeois</p>"

    data = Calendar.from_ical(requests.get("https://wiki.hackerspace.lu/wiki/Special:Ask/-5B-5BCategory:Event-5D-5D-20-5B-5BStartDate::%2B-5D-5D-20-5B-5BStartDate::-3E2014-2D06-2D30-5D-5D/-3FStartDate%3Dstart/-3FEndDate%3Dend/-3FHas-20location/-5B-5BCategory:Event-5D-5D-20-5B-5BStartDate::%2B-5D-5D-20-5B-5BStartDate::-3E2014-2D06-2D30-5D-5D/-3FStartDate%3Dstart/-3FEndDate%3Dend/-3FHas-20location/mainlabel%3D/limit%3D50/order%3DASC/sort%3DStartDate/format%3Dicalendar").content)

    for event in data.walk()[1:]:
        db_event = create_event(
            title=event["SUMMARY"].encode("Utf-8"),
            start=event["DTSTART"].dt.replace(tzinfo=None),
            end=event["DTEND"].dt.replace(tzinfo=None),
            url=event["URL"],
        )

        db_event.tags.add("hackerspace", "luxembourg")


@event_source(background_color="#25272C", text_color="#C58723", key=None, agenda="be", url="http://voidwarranties.be")
def voidwarranties(create_event):
    """
    <p>
    Het is een locatie waar gelijkgestemden kunnen samenwerken aan projecten.
    Soms zijn dit electronica, informatica of gewoon kunstzinnige experimenten. Al
    dit experimenteren, of liever gezegd, hacken heeft maar één doel: de
    hackerspace upgraden tot een plaats die inspireert om nog leukere dingen te
    maken.
    </p>
    <p>
    Een locatie is 1 kant van het verhaal, aan de andere kant zijn er de
    leden en bezoekers, de échte bron van ideeën en kennis.
    </p>
    """

    data = Calendar.from_ical(requests.get("http://voidwarranties.be/index.php/Special:Ask/-5B-5BCategory:Events-5D-5D/-3FHas-20start-20date=start/-3FHas-20end-20date=end/-3FHas-20coordinates=location/format=icalendar/title=VoidWarranties/description=Events-20at-20http:-2F-2Fvoidwarranties.be/limit=500").content)

    for event in data.walk()[1:]:
        title = str(event["SUMMARY"])
        url = event["URL"]
        start = event["DTSTART"].dt if event.get("DTSTART") else event["DTSTAMP"].dt
        end = event["DTEND"].dt if event.get("DTSTART") else None

        db_event = create_event(
            title=title,
            url=url,
            start=start,
            end=end
        )

        db_event.tags.add("hackeragenda")


generic_meetup("webrtc", "WebRTC-crossingborders", background_color="#F99232", text_color="white", agenda="be", tags=["programming", "webrtc", "webdev"], description="""
<p>
As part of a community who believe that WebRTC is a movement for the next
years, we exchange ideas, knowledge and experience, projects on where and how
to apply this new future focused browser-to-browser technology.<br>

Join the enthousiasts about new technologies and business related
opportunities.&nbsp;
</p>
""")


@event_source(background_color="white", text_color="black", agenda="be", url="http://www.0x20.be")
def whitespace(create_event):
    """
    <p>
    <a href="/Whitespace" title="Whitespace">Whitespace</a> (0x20) is a <a
    href="/Documentation" title="Documentation">hackerspace</a> in the wonderful
    city of Ghent, Belgium. It is a physical space run by a group of people
    dedicated to various aspects of constructive &amp; creative hacking. Our <a
    href="/FAQ" title="FAQ">FAQ</a> is an ever growing useful resource of
    information about who we are, what we do and how you can become a part of all
    the <b>awesomeness.</b>  Also check out the hackerspaces in <a class="external
    text" href="http://we.voidwarranties.be">Antwerp</a>, <a class="external text"
    href="http://hackerspace.be/">Brussels</a> and <a class="external text"
    href="http://www.wolfplex.org/">Charleroi</a>.
    </p>
    """
    soup = BeautifulSoup(requests.get("http://www.0x20.be/Main_Page").content)

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

        db_event = create_event(
            title=title,
            url=url,
            start=start,
            end=end,
            location=location.strip() if location else None
        )

        db_event.tags.add("hackerspace")


# @event_source(background_color="#666661", text_color="black")
def wolfplex(create_event):
    html_parser = HTMLParser()
    soup = BeautifulSoup(requests.get("http://www.wolfplex.org/wiki/Main_Page").content)
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

        db_event = create_event(
            title=title,
            url=url,
            start=start,
            location=location
        )

        db_event.tags.add("hackerspace")
