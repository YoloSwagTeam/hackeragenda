# encoding: utf-8

import os
import re
import time
import requests
import feedparser
import dateparser

from bs4 import BeautifulSoup
from bs4.element import NavigableString
from django.template.defaultfilters import slugify
from django.conf import settings
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from icalendar import Calendar
from HTMLParser import HTMLParser

from events.management.commands.fetch_events import event_source
from events.generics import (
    generic_meetup,
    generic_eventbrite,
    generic_google_agenda,
    generic_facebook_page,
    json_api,
)


@event_source(background_color="#f2be79", text_color="#000000", url="http://www.meetup.com/fr/3Dvangelist-professional-workshop-3D-printing/", predefined_tags=[])
def _3dvangelist_professional_workshop_3d_printing():
    """
    <p>Boeiende workshops 3D-printen van theorie tot praktijk Op verschillende locaties in Vlaanderen. Natuurlijk hebt u al gehoord van 3D-printen. Maar nu is de vraag: wat kunt u er eigenlijk mee, zowel professioneel als persoonlijk? Het goede nieuws is dat u dat met de workshops van 3Dvangelist individueel kunt ontdekken. We bieden u een unieke formule en dat op verschillende locaties in Vlaanderen. Doet u mee? Want misschien wist u het nog niet, maar: we zijn allemaal makers. De workshop is ook beschikbaar als in-companytraining op maat of in een formule specifiek voor leerkrachten.</p>
"""
    return generic_meetup("3Dvangelist-professional-workshop-3D-printing")


@event_source(background_color="#133F52", text_color="#FFFFFF", key=None, url="https://groups.google.com/d/forum/afpyro-be")
def afpyro():
    '<p>Les apéros des amateurs du langage de programmation <a href="https://www.python.org/">python</a>.</p>'
    soup = BeautifulSoup(requests.get("http://afpyro.afpy.org/").content)
    filtering = lambda x: x['href'][:7] == '/dates/' and '(BE)' in x.text
    for link in filter(filtering, soup('a')):
        datetuple = map(int, link['href'].split('/')[-1].split('.')[0].split('_'))
        yield {
            'title': link.text,
            'start': datetime(*datetuple),
            'url': "http://afpyro.afpy.org" + link['href'],
            'tags': ("python", "code", "drink", "code")
        }


@event_source(background_color="#3EA86F", text_color="#ffffff", url="http://www.meetup.com/API-Craftsmanship/", predefined_tags=['code', 'craftsmanship', 'api'])
def api_craftsmanship():
    """
    <p>Our objective is to provide API enthusiasts, people who are thinking about, interested in, or actively developing APIs, a space to get together, share ideas, trends, and discuss techniques and technologies. Please come and join us, learn from each other, and have a little fun.</p>
"""
    return generic_meetup("API-Craftsmanship")


@event_source(background_color="#61B132", text_color="#ffffff", url="http://www.meetup.com/BeClojure/", predefined_tags=['code', 'clojure', 'jvm', 'lisp', 'concurency'])
def be_clojure():
    """
    <p>Do you love Lisp? Are you a Functional Programmer already using other languages and curious about Clojure? Are you already using Clojure? Do you want to talk about Clojure with fellow developers in Belgium? Join us!</p>
    <p><a href="http://beclojure.org">http://beclojure.org</a> <br/></p>
"""
    return generic_meetup("BeClojure")


@event_source(background_color="#F99232", text_color="#ffffff", url="http://www.meetup.com/Belgian-Java-User-Group/", predefined_tags=['code', 'java'])
def belgian_java_user_group():
    """
    <p>The primary focus of The Belgium Java User Group (founded in 1997) is to inform our members about the Java ecosystem. We regularly (approximately every 6 weeks) organise sessions to socialize, learn and inspire.</p>
"""
    return generic_meetup("Belgian-Java-User-Group")


@event_source(background_color="#ef4531", text_color="#ffffff", url="http://www.meetup.com/Belgian-Software-Craftsmanship-Guild/", predefined_tags=["code", "craftsmanship", "agile"])
def belgian_software_craftsmanship_guild():
    """
    <p>This community is a breeding ground for lots of cool events involving software engineering. It is open to all people who are passionate about development and strongly believe in mastering the craft of software. Your experience level can be that of a level 1 front end ninja to that of a level 80 embedded software magician. Everybody who believes their craft is something to be proud of and something worth mastering and sharing is welcome to join our ranks.</p>
"""
    return generic_meetup("Belgian-Software-Craftsmanship-Guild")


@event_source(background_color="#133F52", text_color="white", url="http://www.meetup.com/Belgium-Python-Meetup-aka-AperoPythonBe", predefined_tags=("python", "code", "drink"))
def belgium_python_meetup():
    "<p>Belgium Python Meetup aka AperoPythonBe</p>"
    return generic_meetup("Belgium-Python-Meetup-aka-AperoPythonBe")


def agenda_du_libre_be_duplicate(event_query, detail):
    id = detail["url"].split("/")[-1].split("=")[-1]
    event_query.filter(url="http://www.agendadulibre.be/showevent.php?id=%s" % id).delete()
    event_query.filter(url="http://www.agendadulibre.be/events/%s" % id).delete()


@event_source(background_color="#3A87AD", text_color="white", url="http://www.agendadulibre.be", key=agenda_du_libre_be_duplicate)
def agenda_du_libre_be():
    "<p>L'agenda des évènements du Logiciel Libre en Belgique.</p>"
    data = Calendar.from_ical(requests.get("http://www.agendadulibre.be/ical.php?region=all").content)

    for event in data.walk()[1:]:
        yield {
            'title': event["SUMMARY"].encode("Utf-8"),
            'url': event["URL"],
            'start': event["DTSTART"].dt.replace(tzinfo=None),
            'location': event["LOCATION"].encode("Utf-8"),
            'tags': (slugify(event["LOCATION"].encode("Utf-8")), 'libre')
        }


@event_source(background_color="#D2353A", text_color="white", url="http://www.meetup.com/Agile-Belgium")
def agile_belgium():
    """<p>This is the meetup group of the Agile Belgium community. We organize regular drinkups and user group meetings. Come after work and meet people you usually only meet at conferences. Anyone interested in Agile or Lean can join.</p>"""
    return generic_meetup("Agile-Belgium")


@event_source(background_color="#F8981D", text_color="white", url="http://www.meetup.com/AWS-User-Group-Belgium", predefined_tags=["cloud", "amazon", "aws", "sysadmin", "code"])
def aws_user_group_belgium():
    """<p>This is a group for anyone interested in cloud computing on the Amazon Web Services platform. All skills levels are welcome.</p>"""
    return generic_meetup("AWS-User-Group-Belgium")


@event_source(background_color="#F39532", text_color="white", url="www.bbug.be", predefined_tags=["blender", "art", "3D-modeling"])
def belgian_blender_user_group():
    """
    <p>The Belgian Blender User Group is a belgium based community of users of the open source software called <a href="https://www.blender.org/">Blender</a>.</p>
    <p>We are a group of users targeting IRL meetings and organizing workshops and training.</p>
    """
    return generic_google_agenda(
        "https://www.google.com/calendar/ical/7chafqnhlfkjqhp806t1tefsgc%40group.calendar.google.com/public/basic.ics",
        per_event_url_function=lambda event: event["DESCRIPTION"])


@event_source(background_color="#9D3532", text_color="white", url="http://www.meetup.com/The-Belgian-AngularJS-Meetup-Group", predefined_tags=["angularjs", "javascript", "webdev", "code"])
def belgian_angularjs():
    """
    <p>Let's get together for some discussions about the awesome AngularJS framework! I started this group to meet the belgian AngularJS community and share together our experience.</p>
    """
    return generic_meetup("The-Belgian-AngularJS-Meetup-Group")


@event_source(background_color="#1D1D1D", text_color="white", url="http://www.meetup.com/Belgian-node-js-User-Group", predefined_tags=["nodejs", "javascript", "code"], description='<p>This node.js user group gathers the belgian node.js developers so we can improve our skill set and build kick-ass amazing apps.<br><br>For the time being: find us on line at <a href="http://www.shadowmedia.be/nodejs/">http://www.shadowmedia.be/nodejs/</a>.</p>')
def belgian_nodejs_user_group():
    return generic_meetup("Belgian-node-js-User-Group")


@event_source(background_color="#7B6DB0", text_color="white", url="http://www.meetup.com/Belgian-Puppet-User-Group", predefined_tags=["puppet", "sysadmin", "devops", "code"], description="<p>Bringing puppet loving people together on a regular base, to talk about best practices, their experience and have interesting discussions about a great configuration management tool.<br><br>IRC: freenode - #puppet-be</p>")
def belgian_puppet_user_group():
    return generic_meetup("Belgian-Puppet-User-Group")


@event_source(background_color="#E0393E", text_color="white", url="http://www.meetup.com/ruby_belgium/", predefined_tags=["ruby", "code"], description="<p>BRUG is the Belgian Ruby User Group.</p>")
def belgian_ruby_user_group():
    return generic_meetup("ruby_belgium")


@event_source(background_color="#f2d379", text_color="#000000", url="http://www.meetup.com/Belgium-Tableau-Software-Data-Analytics-User-Group-Meetup/", predefined_tags=['code', 'data'])
def belgium_tableau_software_data_analytics_user_group_meetup():
    """
    <p>For people with a passion for exploring, using data analytics. Explorers may be interested sport, health, journalism, science, engineering, politics, government, finance, economics, art, or history, to name but a few. Meetings are mainly conducted in English with a little French and Dutch thrown in.</p>
"""
    return generic_meetup("Belgium-Tableau-Software-Data-Analytics-User-Group-Meetup")


@event_source(background_color="#FEE63C", text_color="#000000", url="http://www.meetup.com/BeScala", predefined_tags=["java", "scala", "jvm", "code"], description="<p>The Belgian Scala User Group.</p>")
def bescala():
    return generic_meetup("BeScala")


@event_source(background_color="DarkGoldenRod", text_color="white", url="http://bhackspace.be")
def bhackspace():
    "<p>The BHackspace is a hackerspace located in Bastogne, Belgium.</p>"
    soup = BeautifulSoup(requests.get("http://wiki.bhackspace.be/index.php/Main_Page").content)

    if soup.table.find('table', 'table') is None:
        return

    for event in soup.find('table', 'table')('tr')[1:]:
        title = event.a.text
        url = "http://wiki.bhackspace.be" + event.a["href"]
        start = parse(event('td')[1].text)
        location = event('td')[2].text

        yield {
            'title': title,
            'url': url,
            'start': start,
            'location': location.strip() if location else "Bastogne",
            'tags': ("hackerspace", "bastogne")
        }


@event_source(background_color="#99c2eb", text_color="#ffffff", url="http://www.meetup.com/fr/Big-Data-Brussels/", predefined_tags=['code', 'bigdata'])
def big_data_brussels():
    """
    <p>An upcoming regular event for people interested in Big Data, whether you are professionals in the field, enthusiasts, or students looking to build your career in that direction. We'll host interesting talks from industry experts, a focus on both business and technical aspects of big data, and plenty of time for networking! </p>
    <p>Big Data, Brussels is hosted and managed by <a href="http://dataconomy.com/">Dataconomy Media GmbH</a>. Please get in touch with events@dataconomy.com if you are interested in participating. <br> </br></p>
    <p><a class="embedded" href="https://www.youtube.com/watch?v=v-ryAXdftUQ">https://www.youtube.com/watch?v=v-ryAXdftUQ</a></p>
"""
    return generic_meetup("Big-Data-Brussels")


@event_source(background_color="black", text_color="white", url="http://www.meetup.com/bigdatabe", predefined_tags=["data", "code", "nosql", "code"], description="<p>Welcome to our Belgian community about bigdata, NoSQL and anything data. If you live or work in Belgium and are interested in any of these technologies, please join! We want you!</p>")
def bigdata_be():
    return generic_meetup("bigdatabe",)


@event_source(background_color="#262626", text_color="#ffffff", url="http://www.meetup.com/fr/Bitcoin-Brussels/", predefined_tags=['bitcoin'])
def bitcoin_brussels():
    """
    <p><strong><span>Welcome to the <em>Bitcoin Brussels</em> group!</span></strong></p>
    <p><strong><span>New members: please join the mailing list - all the discussion happens there! <br> </br></span></strong></p>
    <p><span>The aim is to bring together people that are interested in cryptocurrencies; to promote discussions among people from different fields, having different backgrounds, and therefore different perspectives.</span></p>
    <p><span>We want to create a group that would meet in a friendly and informal way, to discuss any kind of subjects related to blockchains, ranging from technical aspects such as cryptographic concepts and software implementations to high-level reflexions, as the social impact to expect on our societies. The goal is also to find common interests to be explored further, practically creating any kind of experimentation, vulgarization, or business opportunities.</span></p>
    <p><span>We target any kind of audience, whether you have strong expertise to share, you are totally new and curious about bitcoin, or even just want to pass by to have a beer and say hello!</span></p>
"""
    return generic_meetup("Bitcoin-Brussels")


@event_source(background_color="#828282", text_color="white", key=None, url="https://blender-brussels.github.io/")
def blender_brussels():
    '<p>The <strong>Blender-Brussels</strong> − also known as <strong>Blender BPY/BGE workshops</strong> − are a series of monthly work sessions organized by <a href="http://xuv.be">Julien Deswaef</a> (<a href="https://github.com/xuv" class="user-mention">@xuv</a>) and <a href="http://frankiezafe.org">François Zajéga</a> (<a href="https://github.com/frankiezafe" class="user-mention">@frankiezafe</a>) with the aim of providing a regular gathering and knowledge sharing space for artists and coders interested in Python scripting in the context of Blender.</p>'

    soup = BeautifulSoup(requests.get("https://blender-brussels.github.io/").content)

    for entry in soup("article", attrs={"class": None}):
        start = entry.find("time")
        title = entry.text
        url = entry.find("a")["href"]
        start = datetime.strptime(entry.find("time")["datetime"][:-6], "%Y-%m-%dT%H:%M:%S")

        yield {
            'title': title,
            'url': "https:" + url,
            'start': start,
            'tags': ("bruxelles", "blender", "3D-modeling", "art"),
        }


@event_source(background_color="#3C6470", text_color="white", url="http://brixel.be", predefined_tags=["Hackerspace", "hasselt"], description="<p>Brixel HQ is located in Spalbeek near Hasselt and we organise events and meetings every Tuesday and the first and third Friday every month. Although we do not always have something planned, we try to be open as much as we can to stimulate the magic things that just might happen... Meetings start at around 19:00h localtime, but this can vary a bit. There is no fixed closing time. We welcome everybody, young or old, in our Brixel HQ. Come have a look, it's fun!</p>")
def brixel():
    return generic_meetup("Brixel-Hackerspace-Meetup-Spalbeek-Hasselt")


@event_source(background_color="#FF0", text_color="#F00", url="http://brotaru.com/", predefined_tags=["videogame", "code"])
def brotaru():
    """
    BROTARU is a monthly meet up of videogame development people in Brussels!
    """
    return generic_facebook_page('bxl.otaru')


@event_source(background_color="#5b5e68", text_color="white", url="http://www.eventbrite.com/o/databeers-brussels-12058309416", predefined_tags=["brussels", "data"])
def bru_data_beers():
    """
    Databeers gathers all those with an interest in data-based stories in an
    informal and relaxed event, together with the best social lubricant: beer.
    """
    return generic_eventbrite("databeers-brussels-12058309416")


@event_source(background_color="#0c0f11", text_color="#ffffff", url="http://www.meetup.com/fr/BruJUG/", predefined_tags=['code', 'java'])
def brujug():
    """
    <p>Brussels is a great city. Java is an amazing platform to develop with. Wouldn't it be awesome if the two could get mixed?! Well, that's the BruJUG, a local Java User Group where passionate Java developers can, since 2010, attend presentations given by passionate speakers.</p>
    <p>Will it be some technology expert, a "big name" evangelist, or even yourself? Let's join the BruJUG to discover what this year will be made of.</p>
    <p>Oh! One last thing. All the events organized by the BruJUG are FREE!</p>
    <p>Pictures of all events are available on FlickR: <a class="linkified" href="https://secure.flickr.com/brujug/">https://secure.flickr.com/brujug/</a></p>
    <p>Videos of divers sessions can be found here: <a class="linkified" href="https://vimeo.com/channels/brujug">https://vimeo.com/channels/brujug</a></p>
    <p>Fastest news channel: <a class="linkified" href="https://twitter.com/brujug">https://twitter.com/brujug</a></p>
    <p>And we are on LinkedIn!</p>
    <p>Do you want to come for the first time, but worry to be lost and alone in the crowd? No problem, just drop us a nice (private) mail/message and we will take care of you, and we promise to make it as nice and pleasant experience. </p>
    <p><em>Registration to events is required since seats are limited.</em></p>
"""
    return generic_meetup("BruJUG")


@event_source(background_color="#415A6C", text_color="#CBE5F7", url="http://www.meetup.com/Brussels-Cassandra-Users", predefined_tags=["nosql", "jvm", "database", "bruxelles", "code"], description="<p>Open to all those interested in Apache Cassandra, Big Data, Hadoop, Hive, Hector, NoSQL, Pig, and high scalability. Let's get together and share what we know!</p>")
def brussels_cassandra_users():
    return generic_meetup("Brussels-Cassandra-Users")


@event_source(background_color="#CAD9EC", text_color="black", url="http://www.meetup.com/Brussels-Data-Science-Community-Meetup", predefined_tags=["bruxelles", "code", "bigdata"], description='<p>The <strong>Blender-Brussels</strong> − also known as <strong>Blender BPY/BGE workshops</strong> − are a series of monthly work sessions organized by <a href="http://xuv.be">Julien Deswaef</a> (<a href="https://github.com/xuv" class="user-mention">@xuv</a>) and <a href="http://frankiezafe.org">François Zajéga</a> (<a href="https://github.com/frankiezafe" class="user-mention">@frankiezafe</a>) with the aim of providing a regular gathering and knowledge sharing space for artists and coders interested in Python scripting in the context of Blender.</p>')
def brussels_data_science_meetup():
    return generic_meetup("Brussels-Data-Science-Community-Meetup")


@event_source(background_color="#8779f2", text_color="#000000", url="http://www.meetup.com/fr/Brussels-Drupal-Meetup/", predefined_tags=['code', 'drupal', 'php', 'brussels'])
def brussels_drupal_meetup():
    """
    <p>If you are doing Drupal in Brussels or thereabouts and would like to learn and chat about Drupal and would like to meet like minded folk, please join.</p>
    <p>Thanks  :) <br/></p>
"""
    return generic_meetup("Brussels-Drupal-Meetup")


@event_source(background_color="#927f82", text_color="#ffffff", url="http://www.meetup.com/fr/Brussels-lean-coffee/", predefined_tags=['code', 'kanban', 'agile'])
def brussels_lean_coffee():
    """
    <p><span>Each Thursday morning we meet in the centre of Brussels to talk about Lean, Kanban, Agile, TPS, or even Personal Kanban and Discovery Kanban. Join us if you get excited about limiting WIP, visualizing workflow, self-organizing teams, and change or even just want to know more about them.</span> <br/></p>
    <p><i>The meetup is member of the Belgium lean coffee meetups, more locations at <a href="http://www.meetup.com/Belgium-lean-coffee">Belgium lean coffee</a>.</i></p>
"""
    return generic_meetup("Brussels-lean-coffee")


@event_source(background_color="#0324C1", text_color="white", url="http://www.meetup.com/wp-bru", predefined_tags=["bruxelles", "wordpress", "cms", "php", "webdev", "code"], description='<p>A gathering of WordPress users and professionals of all levels.<br><br>Whether you\'re a site owner, designer, developer, plug-in creator all are welcome to attend to learn, share and expand their knowledge of WordPress.<br><br>Have a look at <a href="http://www.meetup.com/wp-bru/about/">our about page</a> for a idea of the type of activities I\'d like to see organised.</p>')
def brussels_wordpress():
    return generic_meetup("wp-bru")


@event_source(background_color="#8179f2", text_color="#000000", url="http://www.meetup.com/fr/BrusselsPHP/", predefined_tags=['code', 'php', 'brussels'])
def brusselsphp():
    """
    <p>This is a group for anyone that has an interest in PHP and that want to meet with like minded people. I hope to see all of you soon.</p>
"""
    return generic_meetup("BrusselsPHP")


@event_source(background_color="#FEED01", text_color="black", url="http://budalab.fikket.com")
def budalab():
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
    data = requests.get("http://budalab.fikket.com/api2/events/calendar.json?start=%s&end=%s" % (now, then)).json()

    for entry in data:
        title = entry["title"]
        start = datetime.strptime(entry["start"][:-6], "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(entry["end"][:-6], "%Y-%m-%dT%H:%M:%S")

        yield {
            'title': title,
            'location': location,
            'url': entry["url"],
            'start': start,
            'end': end,
            'tags': ("fablab",)
        }


@event_source(background_color="white", text_color="#990000", url="http://www.bxlug.be")
def bxlug():
    """
    <p>Le BxLUG est une association d’utilisateurs de logiciels libres créée en 1999 et dont l’objectif est la promotion de GNU/Linux et autres logiciels libres dans la région de Bruxelles.</p>

    <p>Nous proposons régulièrement des activités conviviales&nbsp;:<br><img src="squelettes-dist/puce.gif" class="puce" alt="-" height="11" width="8">&nbsp;<a href="spip.php?article13" class="spip_in">Linux Copy Party</a><br><img src="squelettes-dist/puce.gif" class="puce" alt="-" height="11" width="8">&nbsp;<a href="spip.php?article10" class="spip_in">Atelier Info Linux</a></p>

    <p>Nous proposons également <a href="spip.php?rubrique8" class="spip_in">des listes de discussion ouvertes</a>  pour l’entraide quotidienne.</p>

    <p><a href="spip.php?rubrique4" class="spip_out">Nos rencontres aident tout un chacun à installer et configurer des systèmes libres, à approfondir leurs connaissances et à découvrir de nouveaux horizons</a></p>
    """
    now = int(time.time())
    then = now + (60 * 60 * 24 * 14)

    data = requests.get("http://www.bxlug.be/spip.php?page=calendrier_quete.json&start=%s&end=%s&_=%s" % (now, then, now)).json()

    for event in data:

        # [:-1] => ignore timezones, because sqlite doesn't seem to like it
        start = parse(event["start"])
        end = parse(event["end"])
        title = event["title"]
        url = os.path.join("http://www.bxlug.be/", event["url"])
        # location = entry.find("p", "location")("span")[1].text.split("Contact")[0].split(":", 1)[1].strip() if entry.find("p", "location") else None

        yield {
            'title': title,
            'url': url,
            'start': start,
            # 'location': location,
            'end': end,
            'tags': ("lug", "bruxelles", "libre")
        }


@event_source(background_color="#FFFFFF", text_color="black", url="https://c3l.lu/", predefined_tags=["hackerspace", "Luxembourg"])
def c3l():
    """
    <p>Funded in 1981, the Chaos Computer Club did not only invade Hamburg and Berlin with its strong idealistic views on hacktivism or network politics, but reached far over the national borders. It was, and still is, an inspiration to many people in the world. Thus, also the reason for funding its own local 'branch' in Luxembourg. </p>
    """
    feed = feedparser.parse("http://ical2atom.c3l.lu/")
    for entry in feed.entries:
        yield {
            'title': entry.title,
            'url': entry.link,
            'start': parse(entry.updated).replace(tzinfo=None),
        }


@event_source(background_color="#D2C7BA", text_color="black", key=None, url="http://www.constantvzw.org")
def constantvzw():
    """
    <p><strong>Constant is a non-profit association, an interdisciplinary arts-lab based and active in Brussels since 1997.</strong></p>

    <p>Constant works in-between media and art and is interested in the culture and ethics of the World Wide Web. The artistic practice of Constant is inspired by the way that technological infrastructures, data-exchange and software determine our daily life. Free software, copyright alternatives and (cyber)feminism are important threads running through the activities of Constant.</p>

    <p>Constant organizes workshops, print-parties, walks and ‘Verbindingen/Jonctions’-meetings on a regular basis for a public that’s into experiments, discussions and all kinds of exchanges.</p>
    """
    soup = BeautifulSoup(requests.get("http://www.constantvzw.org/site/?page=agenda").content, "html5lib")

    for event in soup.find("div", "liste-items evenements")("div", "box"):
        title = event("h3")[1].text
        url = "http://www.constantvzw.org/site/" + event.a["href"]

        if re.search(",\d+\.html", url):
            continue

        location = event.find("p", itemprop="location").text.replace("\n", " ") if event.find("p", itemprop="location") else None

        start = parse(event.find("abbr", "dtstart")["title"]).replace(tzinfo=None)
        end = parse(event.find("abbr", "dtend")["title"]).replace(tzinfo=None)

        yield {
            'title': title,
            'url': url,
            'start': start,
            'end': end,
            'location': location.strip() if location else None,
            'tags': ("artist", "libre", "art"),
        }


@event_source(background_color="black", text_color="#FFC3A0", url="http://www.ooooo.be/daemonsshellscripts/", key=None)
def daemons_shell_scripts():
    "Dæmons & Shell Scripts"
    if not hasattr(settings, "OOOOO_CREDENTIALS"):
        print "ERROR: no OOOOO_CREDENTIALS in settings, disabling daemons_shell_scripts"
        return

    root = "http://%s@ooooo.be" % settings.OOOOO_CREDENTIALS

    soup = BeautifulSoup(requests.get(root + "/cloud/remote.php/caldav/calendars/hackeragenda/hackeragenda_shared_by_ooooo").content, "html5lib")
    for ics in set([x["href"] for x in soup("a") if x["href"].endswith(".ics")]):

        data = Calendar.from_ical(requests.get(root + ics).content)

        for event in data.walk()[1:]:
            if "SUMMARY" not in event or "DTSTART" not in event:
                continue

            yield {
                'title': event["SUMMARY"].encode("Utf-8"),
                'url': "http://www.ooooo.be/daemonsshellscripts/",
                'start': event["DTSTART"].dt.replace(tzinfo=None),
                'end': event["DTEND"].dt.replace(tzinfo=None) if "DTEND" in event else None,
                'location': event["LOCATION"].encode("Utf-8") if "LOCATION" in event else None,
                'tags': (slugify(event.get("LOCATION", "").encode("Utf-8")), 'libre') + tuple(event.get("CATEGORIES", "").split(", "))
            }


@event_source(background_color="#0095CB", text_color="#ffffff", url="http://www.meetup.com/dddbelgium/", predefined_tags=['code', 'ddd'])
def ddd_belgium():
    """
    <p>We are a group of software developers, ranging from noobs to veterans, who meet up regularly at different places in Belgium. We aim to spread the ideas of Domain-Driven Design, and become better Software Craftsmen, by teaching and learning. We are technology-agnostic. We are open, self-organized, and inclusive. Everybody is invited to join and participate!</p>
    <p> <br/></p>
    <p><a href="mailto:mathias@verraes.net">Contact us</a> if you want to sponsor us or speak at a meetup.</p>
"""
    return generic_meetup("dddbelgium")


@event_source(background_color="#e3a030", text_color="#ffffff", url="http://www.meetup.com/fr/Devoxx4Kids-BE/", predefined_tags=['code', 'kids', 'education'])
def devoxx4kids_be():
    """
    <p>L'ASBL Devoxx4Kids est axée sur l'éducation des parents afin qu'ils montrent à leurs enfants qu'il est possible de faire quelque chose de plus créatif avec les ordinateurs. L'objectif est d'introduire les parents et leurs enfants à la programmation, de la robotique et de l'ingénierie d'une façon amusante. Pour ce faire, l'ASBL Devoxx4Kids organise des sessions où les participants peuvent développer des jeux informatiques, programmer des robots et ont également une introduction à l'électronique. </p>
    <p><span>De Devoxx4Kids VZW richt zich op het opleiden van ouders om hun kinderen te laten zien dat het mogelijk is om iets meer creatief met computers doen. Het doel is om ouders en hun kinderen te programmeren, robotica en engineering te introduceren op een leuke manier. Om dit te doen, organiseert de VZW Devoxx4Kids sessies waarin deelnemers computer games, programma robots kunnen ontwikkelen en hebben ook een inleiding tot de elektronica.</span> <br/></p>
"""
    return generic_meetup("Devoxx4Kids-BE")


@event_source(background_color="#7B6DB0", text_color="#ffffff", url="http://www.meetup.com/devspace-elixir-study-group/", predefined_tags=['code', 'elixir', 'concurency'])
def devspace_elixir_study_group():
    """
    <p>We just get together and learn ourselves some Elixir for greater good.</p>
    <p>Follow us on Twitter <a href="https://twitter.com/elixir_be">@elixir_be</a>.</p>
"""
    return generic_meetup("devspace-elixir-study-group")


@event_source(background_color="#008FC4", text_color="white", url="http://www.meetup.com/Docker-Belgium", predefined_tags=["docker", "lxc", "sysadmin", "devops", "code"], description='<p>Meet other developers and ops engineers using Docker.&nbsp;Docker is an open platform for developers and sysadmins to build, ship, and run distributed applications. Consisting of Docker Engine, a portable, lightweight runtime and packaging tool, and Docker Hub, a cloud service for sharing applications and automating workflows, Docker enables apps to be quickly assembled from components and eliminates the friction between development, QA, and production environments. As a result, IT can ship faster and run the same app, unchanged, on laptops, data center VMs, and any cloud.</p><p>Learn more about Docker at&nbsp;<a href="http://www.docker.com/">http://www.docker.com</a></p>')
def docker_belgium():
    return generic_meetup("Docker-Belgium")


@event_source(background_color="#FC745D", text_color="white", url="http://www.meetup.com/Ember-js-Brussels", predefined_tags=["emberjs", "javascript", "code", "webdev"], description="This is a group for anyone interested in developing web applications in Ember.js. I created this group because it's nice to have a local community for sharing knowledge, ideas and inspiration about this awesome web framework. The learning curve for Ember.js is not the lightest so it will also be a place to share your frustrations! Beginner or expert, everyone is welcome.")
def ember_js_brussels():
    return generic_meetup("Ember-js-Brussels")


@event_source(background_color="#f2a579", text_color="#000000", url="http://www.meetup.com/fr/Fab-Brol-Mons/", predefined_tags=['fablab', 'mons'])
def fab_brol_mons():
    """
    <p>Si vous aimez bidouiller des raspberry pi, des Arduino, des breadboards etc etc et que vous cherchez des personnes avec qui passer un peu de temps pour améliorer vos idées alors rejoignez-nous !</p>
    """
    return generic_meetup("Fab-Brol-Mons")


@event_source(background_color="#f2798e", text_color="#000000", url="http://www.meetup.com/FabLabBornem/", predefined_tags=['fablab', 'bornem'])
def fablab_bornem():
    """
    <p>Wij willen een FabLab oprichten in Bornem en we hebben al een naam: FabLab Bornem :-) In een FabLab kan je zelf iets maken, dankzij 3D printers, lasercutters, electronica, sensoren, robots, ... Wat hebben we nodig: (A) een locatie (in een school, in een bedrijf, ...) om het FabLab in te richten (B) enthousiaste vrijwilligers om mee aan de kar te trekken tijdens opstart en nadien begeleiders voor tijdens de openingsuren van het FabLab (bijv. woensdagnamiddag, vrijdagavond) (C) sponsors voor aankoop hardware en software.</p>
"""
    return generic_meetup("FabLabBornem")


@event_source(background_color="white", text_color="#515151", url="http://www.fablabcharleroi.be/", predefined_tags=["fablab", "charleroi"])
def fablab_charleroi():
    """
    Ensuite dans l’esprit que nous voulons mettre en place les mots qui me viennent spontanément : Fun, partage, passion, soutien, entre aide, technique, développement, innovation,…
    Cette liste non-exhaustive doit vous mettre sur la piste de nos objectifs au sein du fablab de Charleroi.
    Le Fablab fait partie d’un ensemble plus grand, le bubble hub qui est un espace créatif qui se décompose en plusieurs activités dont celle du fablab : http://bubblehub.be/susciter-la-creativite/fablab/
    """
    return generic_google_agenda("https://calendar.google.com/calendar/ical/2qpt4enmk3brsvmkmitko7b3hg%40group.calendar.google.com/public/basic.ics")


@event_source(background_color="#e8e8e8", text_color="#2ba6ab", url="http://fablabmons.be/", predefined_tags=["fablab", "mons"])
def fablab_mons():
    """
    « Concevez-le et fabriquez-le vous-mêmes ! »
    Voilà ce que proposent les « FabLabs » aux étudiants, aux chercheurs, aux designers, aux artistes, aux roboticiens, aux entrepreneurs et à tous les bricoleurs du 21e siècle qui veulent passer rapidement d’une idée à un prototype pour promouvoir leur projet.
    La particularité du projet montois, initié au sein de l’Université de Mons, est en effet d’être porté par une diversité d’acteurs dont les besoins sont finalement très complémentaires. Le « FabLab Mons » est avant tout orienté grand public, formation et recherche.
    """
    return generic_google_agenda("https://calendar.google.com/calendar/ical/7j8q9f7sjerkg8im1q3s0sp27o%40group.calendar.google.com/public/basic.ics")


@event_source(background_color="#C9C4BF", text_color="black", key=None, url="http://fo.am")
def foam():
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

    soup = BeautifulSoup(requests.get("http://fo.am/events/").content, "html.parser")

    for line in soup.find('table', 'eventlist')('tr')[1:]:
        title, event_date = line('td')

        link = title.a['href']

        dates = map(parse, event_date.text.split('-'))
        if len(dates) == 2:
            start, end = dates
        else:
            start, end = dates[0], None

        soupsoup = BeautifulSoup(requests.get('http://fo.am' + link).content)

        if soupsoup.find("h3", text="Location"):
            location = re.sub(" +", " ", soupsoup.find("h3", text="Location").next_sibling.next_sibling.text.strip().replace("\n", " "))
        else:
            location = None

        tags = ["art"]
        if "FoAM Apéro" in title.text:
            tags.append('meeting')

        yield {
            'title': title.text,
            'url': 'http://fo.am' + link,
            'location': location,
            'start': start,
            'end': end,
            'tags': tags
        }


@event_source(background_color="#1565C0", text_color="#ffffff", url="http://gdg.brussels/", predefined_tags=['code'])
def gdg_brussels():
    """
    <p>Google Developer Group is an English speaking group of developers and engineers that meet once a month since 2009 to share, learn and code with Android, Dart, Polymer and other Google Technologies. The main purpose is to get to know other developers and to exchange knowledge and hear about the latest features of new technologies.</p>
    <p>The group is independent of Google. The organizers are not working for Google. Still, we have a good relationship.</p>
    """
    return generic_meetup("gdg-brussels")


@event_source(background_color="#6C7DB6", text_color="#ffffff", url="http://www.meetup.com/Hasselt-PHP-Meetup/", predefined_tags=['code', 'php', 'hasselt'])
def hasselt_php_meetup():
    """
    <p>Join us to meet other PHP developers in Hasselt (and surrounding cities) in our monthly Meetup. Learn new things, make new connections and have fun!</p>
"""
    return generic_meetup("Hasselt-PHP-Meetup")


@event_source(background_color="coral", text_color="white", key=None, url="https://hackerspace.be")
def hsbxl():
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
        tags = ["hackerspace"]
        if "TechTue" in event["fulltext"] or "Garbage day" in event["fulltext"]:
            tags.append("meeting")

        yield {
            'title': event["fulltext"],
            'url': event["fullurl"],
            'start': datetime.fromtimestamp(int(event["printouts"]["Start date"][0])),
            'end': datetime.fromtimestamp(int(event["printouts"]["End date"][0])),
            'location': event["printouts"]["Location"][0]["fulltext"],
            'tags': tags
        }


@event_source(background_color="#b8ada0", text_color="#ffffff", url="http://www.meetup.com/Icon-Brussels-research-and-education-group/", predefined_tags=['art'])
def icon_brussels_research_and_education_group():
    """
    <p>Hi! This is the place to announce and discuss events, free try-out courses and meetups organised by Icon-Brussels, an innovative research and learning centre for art and contemporary technology, based in the heart of Brussels, Europe. You can find out about masterclasses with topics like Adobe After Effects, Film Art, Arduino, Processing for Visual Art, Logo Design, and much, much more. We will be updating the eventlist regularly. You'll be invited for one-time lectures, concerts and anything to do with technological innovation and entrepreneurship.</p>
"""
    return generic_meetup("Icon-Brussels-research-and-education-group")


@event_source(
    background_color="#F47D31", text_color="white", url="http://www.imal.org/fablab/",
    predefined_tags=["fablab", "art"],
    description="""
    <p>iMAL (interactive Media Art Laboratory), is a non-profit association
    created in Brussels in 1999, with the objective to support artistic forms
    and creative practices using computer and network technologies as their
    medium. In 2007, iMAL opened its new venue: a Centre for Digital Cultures
    and Technology of about 600m2 for the meeting of artistic, scientific and
    industrial innovations. A space entirely dedicated to contemporary artistic
    and cultural practices emerging from the fusion of computer,
    telecommunication, network and media.</p>
    """)
def imal():
    return generic_google_agenda("https://www.google.com/calendar/ical/8kj8vqcbjk4o7dl26bvi6lm3no%40group.calendar.google.com/public/basic.ics")


@event_source(background_color="#296038", text_color="#6FCE91", url="http://www.incubhacker.be")
def incubhacker():
    "<p>Incubhacker est un hackerspace basé dans la région namuroise, c'est un espace de rencontre et de création interdisciplinaire.</p>"

    soup = BeautifulSoup(requests.get("http://www.incubhacker.be/?page=1").content, "html5lib")

    if soup("a", "iCtip", href=lambda x: x and x.startswith("http://www.incubhacker.be/?page=")):
        pages_number = int(soup("a", "iCtip", href=lambda x: x and x.startswith("http://www.incubhacker.be/?page="))[-1].text)
    else:
        pages_number = 1

    for page_number in range(1, pages_number + 1):
        soup = BeautifulSoup(requests.get("http://www.incubhacker.be/?page=%s" % page_number).content, "html5lib")

        for event in soup("div", "ic-content"):
            title = event.h2.text.strip()
            url = "http://www.incubhacker.be" + event.h2.a["href"]

            date = event.find("span", "ic-period-startdate").text
            start_time = event.find("span", "ic-single-starttime").text
            end_time = event.find("span", "ic-single-endtime").text

            start = dateparser.parse(date + " " + start_time)
            end = dateparser.parse(date + " " + end_time)

            tags = ["hackerspace"]
            if title.strip() == u'S\xe9ance hebdomadaire normale':
                tags.append("meeting")

            yield {
                'title': title,
                'url': url,
                'start': start,
                'end': end,
                'tags': tags
            }


@event_source(background_color="#79f2e1", text_color="#000000", url="http://www.meetup.com/Internet-of-Things-Ghent/", predefined_tags=['code', 'iot', 'ghent'])
def internet_of_things_ghent():
    """
    <p><i>Co-organizer: Johan Thys (I-minds).</i></p>
    <p><span>This group wants to flush out Internet of Things projects in Ghent, Antwerp, Leuven and Brussels in order to create synergies and interoperability of levels of infrastructure. It also wants to bring in endusers into this process. It is aligned with the FP 7 Project Sociotal.eu that is aiming at building an ecosystem of citizen centric services. Its pilot cities are Novi Sad and (Smart) Santander.</span> <br> </br></p>
"""
    return generic_meetup("Internet-of-Things-Ghent")


@event_source(background_color="#79c1f2", text_color="#000000", url="http://www.meetup.com/fr/Internet-of-Things-IoT-Leuven/", predefined_tags=['iot', 'code', 'leuven'])
def internet_of_things_iot_leuven():
    """
    <p>Executive summary still to come :-) .... but if you're interested in any aspects of "the Internet Of Things" and are willing to share, discuss, engage with us feel free to join our group and attend one of our events. </p>
    <p>If there's one revolutionary technology out there that you don't want to miss #IoT is just that . </p>
    <p>It is my intention not only to have peer2peer discussions but also to have presentations from industry speakers and influencers on this subject.</p>
    <p>Don't forget to spread the word onto other IoTGroupies!</p>
    <p>Hope to CU soon ~ Bart</p>
    <p> <br/></p>
"""
    return generic_meetup("Internet-of-Things-IoT-Leuven")


@event_source(background_color="#CE112C", text_color="#ffffff", url="http://www.meetup.com/iot_be/", predefined_tags=['code', 'iot'])
def iot_be():
    """
    <p><span>This meetup is dedicated to the design practices, technologies, insights and opportunities around the next frontier information access - the Internet of Things (IoT). We want to cross-pollinate ideas from engineers, designers, researchers, data scientists and entrepreneurs to create meaningful and tangible solutions that will make information access more human, ubiquitous and commercially viable.</span></p>
    <p><span>Follow us on Twitter: @iot_be (#iot_be)</span></p>
"""
    return generic_meetup("iot_be")


@event_source(background_color="#ffde17", text_color="#000000", url="http://www.meetup.com/javascriptlab/", predefined_tags=['javascript', 'code'])
def javascriptlab():
    """
    <p>We love JavaScript and we thought it would be a great idea to put together a place where people can talk, meet and share their knowledge to bring their skills to the next level.  <br>So join us and let's get better at doing this, together.</br></p>
"""
    return generic_meetup("javascriptlab")


@event_source(background_color="#579FAB", text_color="black", url="http://www.meetup.com/Jeudis-du-Libre-Mons", predefined_tags=["mons-hainaut", "libre"], description="<p>La création des Jeudis du Libre est l’initiative de jeunes administrateurs systèmes désireux de communiquer sur Les Logiciels Libres. Tout les troisièmes jeudis du mois, un programme issu du travail de développeurs à travers le monde, est présenté aux administrateurs systèmes, aux amateurs d’informatique, aux professeurs ou encore aux simples curieux.</p>")
def jeudi_du_libre_mons():
    return generic_meetup("Jeudis-du-Libre-Mons")


@event_source(background_color="#FFFFFF", text_color="#FB503B", url="http://www.meetup.com/Laravel-Brussels", predefined_tags=["bruxelles", "laravel", "php", "webdev", "code"], description='<p>A group for anyone interested in learning about and sharing knowledge on Laravel, the "PHP framework for web artisans". The group welcomes beginners and experts, amateurs and pros, young and old, etc. Laravel is an accessible, yet powerful framework for web application development. Its expressive, elegant syntax and its clean structure make PHP development a real joy. As the Laravel community keeps growing, this group is an attempt to get Belgium-based users to know each other, and to spread the word!</p>')
def laravel_brussels():
    return generic_meetup("Laravel-Brussels")


@event_source(background_color="#C9342C", text_color="#ffffff", url="http://www.meetup.com/Le-Wagon-Brussels-Coding-Station/", predefined_tags=["code", "education"])
def le_wagon_brussels_coding_station():
    """
    <p>Our program is designed for complete beginners or "half-beginners" who really want to dive into programming and, above all, change their mindset. Learn to think like a developer, consider issues with new insight, and become more creative thanks to these newly acquired abilities. Our unique goal is to facilitate becoming an outstanding entrepreneur who is able to code his/her own projects and to deeply understand technical issues.</p>
"""
    return generic_meetup("Le-Wagon-Brussels-Coding-Station")


@event_source(background_color="#37C2F1", text_color="black", url="http://www.meetup.com/Les-mardis-de-lagile-Bruxelles", predefined_tags=["bruxelles", "agile", "code", "drink"], description="<p>Appel à la communauté agile de Bruxelles ! Que vous soyez un fervent agiliste ou tout simplement intéressé par l'agilité, venez découvrir de nouvelles approches, vous enrichir à travers les nombreuses sessions proposées, participer à des innovation games et partager vos retours d'expérience lors de nos meetups \"Les Mardis de l'agile\" !</p>")
def les_mardis_de_l_agile():
    return generic_meetup("Les-mardis-de-lagile-Bruxelles")


@event_source(background_color="#d1c4b8", text_color="#ffffff", url="http://www.meetup.com/fr-FR/Leuven-Lean-coffee/", predefined_tags=[])
def leuven_lean_coffee():
    """
    <p>Each Month we meet in Leuven to talk about Lean, Kanban, Agile, TPS, or even Personal Kanban and Discovery Kanban. Join us if you get excited about limiting WIP, visualizing workflow, self-organizing teams, and change or even just want to know more about them. The meetup is member of the Belgium lean coffee meetups, more locations at Belgium lean coffee.</p>
"""
    return generic_meetup("Leuven-Lean-coffee")


@event_source(background_color="#3EA86F", text_color="white", url="http://www.meetup.com/MongoDB-Belgium", predefined_tags=["mongodb", "database", "code"])
def mongodb_belgium():
    """
    <p>The first countrywide MongoDB user group in Belgium. Meetups will be held every 3 months. Talk proposals can be sent to hannes@showpad.com.</p>
    """
    return generic_meetup("MongoDB-Belgium")


@event_source(background_color="#b0b0b0", text_color="#66182b", url="http://nadine.be")
def nadine():
    """
    nadine est un labortoire bruxellois pour les arts actuels transdisciplinaires.
    Grâce aux résidences in-situ, les projets de recherches, ou les ateliers, les artistes disposent d'espace pour s'exprimer.
    nadine soutient les performances, l'art dans les lieux publics, les installations multimedia, les projets expérimentaux où les frontières de la création/production, recherche et présentation s'estompent

    <i>(traduits du néerlandais par iTitou)</i>
    """
    soup = BeautifulSoup(requests.get('http://nadine.be/what/event').content)
    for cell in soup.select('td'):
        if not cell.select(".from-date"):
            continue

        from_date = parse(cell.select('.from-date')[0].select('.date-display-single')[0]['content']).replace(tzinfo=None)
        to_date = parse(cell.select('.to-date')[0].select('.date-display-single')[0]['content']).replace(tzinfo=None)
        title_dom = cell.select('.views-field-title a')[0]
        title = title_dom.text.strip()
        url = title_dom['href']
        tags = ['art'] + cell.select('.views-field-field-freetags .field-content')[0].text.split()

        yield {
            'title': title,
            'url': url,
            'start': from_date,
            'end': to_date,
            'tags': tags
        }


@event_source(background_color="indigo", text_color="white", url="https://npbx.wordpress.com/category/npbbxl/")
def npbbxl():
    '''
    <p>A NetPoliticsBeerX (#nbpx) is an informal meetup of people involved or interested in the different fields of internet politics and activism (e.g. copyright, privacy, open data, net neutrality, …).</p>
    <p>It all started in Berlin with the legendary #npbb and spread from there to Düsseldorf (<a href="http://twitter.com/sixtus/status/25290063331983360">#npbd</a>),&nbsp;Bruxelles (<a href="http://doodle.com/3ev9zcu87uts522m">#npbbxl</a>) and whoknowswhatsnext.</p>
    '''
    for event in feedparser.parse("https://npbx.wordpress.com/category/npbbxl/feed/").entries:
        # before this date, the events doesn't respect the format
        if parse(event["published"]).replace(tzinfo=None) < parse("28/02/15"):
            continue

        title, date, _, location = re.match("(.+) (\d+/\d+/\d+ at \d+(\.\d+)? ?[ap]m), (.+)", event["title"]).groups()
        date, time = map(parse, date.replace(".", "h").split(" at "))
        date = date.replace(hour=time.hour).replace(minute=time.minute)

        yield {
            "title": title,
            "url": event["link"],
            "start": date,
            "tags": ["politic", "netpolitic", "activism"],
        }


@event_source(background_color="DarkBlue", text_color="white", url="http://neutrinet.be")
def neutrinet():
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

        tags = ["network", "isp"]
        if "Meeting" in title:
            tags.append("meeting")

        yield {
            'title': title,
            'url': url,
            'start': start,
            'location': location.strip() if location else None,
            'tags': tags
        }


@event_source(background_color="#299C8F", text_color="white", url="https://www.google.com", predefined_tags=["opendata"])
def okfnbe():
    """
    <p>Open Knowledge Belgium is a not for profit organisation (vzw/asbl) ran
    by a board of 6 people and has currently 1 employee. It is an umbrella
    organisation for Open Knowledge in Belgium and, as mentioned below, contains
    different working groups of people working around various projects.</p>

    <p>If you would like to have your activities under our wing, please contact us at our mailinglist.</p>
    """
    return generic_google_agenda("https://www.google.com/calendar/ical/sv07fu4vrit3l8nb0jlo8v7n80@group.calendar.google.com/public/basic.ics")


@event_source(background_color="#FFFFFF", text_color="#00AA00", url="http://www.okno.be")
def okno():
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

        soupsoup = BeautifulSoup(requests.get(link).content)

        maybe_end = soupsoup.find("div", "date").text.split("|")[0].strip().split(u"\u2014")[1:]
        if maybe_end:
            maybe_end = parse(maybe_end[0].strip())
        else:
            maybe_end = None

        yield {
            'title': title,
            'url': link,
            'start': datetime(*datetuple),
            'end': maybe_end,
            'location': soupsoup.find("div", "date").text.split("|")[-1].strip(),
            'tags': ("art",)
        }


def opengarage_duplicated(event_query, detail):
    events = [event for event in event_query.all() if not event.url.split("/")[-2].isdigit()]
    map(lambda x: x.delete(), events)
    event_query.filter(url=detail["url"]).delete()


def opengarage_meetings(event):
    return ('meeting',) if event.title == "Open Garage" else tuple()


@event_source(background_color="DarkOrchid", text_color="white", url="http://www.meetup.com/OpenGarage", predefined_tags=["hackerspace", opengarage_meetings], key=opengarage_duplicated)
def opengarage():
    '''
    <p>The "Open Garage" is a double garage in Borsbeek, Belgium, some sort of <a href="http://en.wikipedia.org/wiki/Hackerspace">hackerspace</a>, where I (<a href="https://plus.google.com/u/2/+AnthonyLiekens/posts">Anthony Liekens</a>) host weekly workshops and many of my projects.
    The garage is open every Thursday evening to everyone who wants to join our community\'s numerous hacking projects.</p>
    <p>Don\'t listen to me, but check out the media\'s reviews of the Open Garage:</p>
    <ul>
    <li><a href="http://hackaday.com/2013/10/22/hackerspacing-in-europe-garage-space-in-antwerp/">Hackaday\'s review of the Open Garage</a></li>
    <li><a href="http://anthony.liekens.net/pub/gva20140614.pdf">The Open Garage in GvA\'s Citta</a> (Belgian newspaper)</li>
    <li><a href="https://www.youtube.com/watch?v=aCuUv5ltw6g">The Open Garage in "Iedereen Beroemd"</a> (Belgian national TV)</li>
    <li><a href="http://www.radio1.be/programmas/de-bende-van-einstein/binnenkijken-de-garage-van-anthony-liekens">The Open Garage on Radio 1</a> (Belgian national radio)</li>
    <li><a href="http://krant.tijd.be/ipaper/20140215#paper/sabato_nl/50">The Open Garage in De Tijd</a> (Belgian "Times" newspaper)</li>
    </ul>
    '''
    return generic_meetup("OpenGarage")


@event_source(background_color="#7B6DB0", text_color="#ffffff", url="http://www.meetup.com/OpenStreetMap-Belgium/", predefined_tags=['osm', 'carto'])
def openstreetmap_belgium():
    """
    <p>This group is all about OpenStreetMap, the best and most popular webmapping project out there! Meet other OpenStreetMappers in these meetups and learn how to contribute to or use OpenStreetMap.</p>
"""
    return generic_meetup("OpenStreetMap-Belgium")


@event_source(background_color="#3987CB", text_color="white", url="http://www.opentechschool.org", predefined_tags=["learning", "code", "bruxelles"])
def opentechschool():
    '''
    <p>OpenTechSchool is a community initiative offering free programming workshops
    and meetups to technology enthusiasts of all genders, backgrounds, and
    experience levels. It supports volunteer coaches in setting up events by taking
    care of the organizational details, encouraging coaches to create original
    teaching material.</p>
    <p>Everyone is invited to participate, whether as a coach or a learner in this
    friendly learning environment where no one feels shy about asking any
    questions.</p>
    '''
    return generic_meetup("OpenTechSchool-Brussels")


@event_source(background_color="#4366AF", text_color="white", predefined_tags=["security"], url="https://www.owasp.org/index.php/Belgium")
def owaspbe():
    '''
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
    '''
    return generic_eventbrite("owasp-belgium-chapter-1865700117")


@event_source(background_color="#757AB2", text_color="#ffffff", url="http://www.meetup.com/php-wvl/", predefined_tags=['code', 'php'])
def php_wvl():
    """
    <p>A PHP Usergroup for all PHP devs based in West-Vlaanderen.</p>
"""
    return generic_meetup("php-wvl")


@event_source(background_color="#0c0024", text_color="#ffffff", url="http://www.meetup.com/fr/phpantwerp/", predefined_tags=['code', 'php'])
def php_antwerp():
    """
    <p>We just started this meetup group. We don't have a regular schedule but we try to organise a meetup now and then. Want to organise a meetup in Antwerp but don't know how/where to start? Contact us and we'll help you out!</p>
"""
    return generic_meetup("phpantwerp")


@event_source(background_color="#015074", text_color="white", url="http://www.meetup.com/phpbenelux", predefined_tags=["php", "code", "webdev"])
def phpbenelux():
    """<p>PHPBenelux user group meetings are a fun way to learn about best practices and new innovations from the world of PHP and to hang out with other PHP developers</p>"""
    return generic_meetup("phpbenelux")


@event_source(background_color="#0082B1", text_color="#ffffff", url="http://www.meetup.com/RBelgium/", predefined_tags=['code', 'r', 'data'])
def r_belgium():
    """
    <p>R community in Belgium. Events, news are here !</p>
"""
    return generic_meetup("RBelgium")


@event_source(background_color="#ef4e30", text_color="#ffffff", url="http://www.meetup.com/fr/ReactJS-Belgium/", predefined_tags=['code', 'web', 'reactjs', 'javascript'])
def reactjs_belgium():
    """
    <p>For more than a year now, React.js has changed the way we think about client-side applications through concepts such as the virtual dom, one-way data flow, immutable data structures and isomorphism.</p>
    <p>ReactBelgium is the occasion to meet those who are building things with React, demo your work, learn from each other and help build the future of the web together!</p>
"""
    return generic_meetup("ReactJS-Belgium")


@event_source(background_color="#36c0cb", text_color="black", url="http://realizebxl.be/", predefined_tags=["makerspace", "bruxelles"])
def realize():
    """
    <p><strong>Realize</strong> est un atelier partagé<a title="plan" href="https://www.google.be/maps/preview#!q=Rue+du+M%C3%A9tal+32%2C+Saint-Gilles&amp;data=!4m10!1m9!4m8!1m3!1d23940!2d4.802835!3d50.988438!3m2!1i1920!2i912!4f13.1" target="_blank"> situé à Saint-Gilles</a>, à deux pas du Parvis. Tous ceux qui veulent réaliser des objets peuvent y accéder grâce à diverses <a href="http://realizebxl.be/inscription/">formules d’abonnement</a>.</p>
    """
    return generic_eventbrite("realize-6130306851")


@event_source(background_color="#0f5021", text_color="#ffffff", url="http://www.meetup.com/fr/RedHat-Belgium/", predefined_tags=['redhat', 'code', 'sysadmin'])
def redhat_belgium():
    """
    <p>This group is about Red Hat Belgium organizing technical events like TUG and hands-on labs on technologies like Openstack, Openshift, JBOSS middleware, Gluster, Ceph etc. <br/></p>
    <p>There will be a mix of hands-on learning labs and informational sessions. <br/></p>
    <p>Please join this group if you're a Red Hat customer or if you follow Red Hat's solutions. It's the ideal opportunity to meet people from Red Hat and to talk to other Red Hat customers on how they run and operate their IT environments. <br/></p>
    <p> <br/></p>
"""
    return generic_meetup("RedHat-Belgium")


@event_source(background_color="#2BC884", text_color="white", url="http://www.relab.be", predefined_tags=["fablab"])
def relab():
    """
    <p><strong>Le RElab, premier Fab Lab de Wallonie, est un atelier numérique ouvert au public et une structure de développement créatif local.</strong>
    La spécificité du RElab réside dans l’utilisation de matériaux de récupération comme matière première et dans l’étude de nouveaux procédés sociaux,
    créatifs et économiques d’upcycling, en liaison avec les nouveaux moyens&nbsp;de fabrication et de communication numérique.</p>
    """
    return generic_google_agenda("https://www.google.com/calendar/ical/utmnk71g19dcs2d0f88q3hf528%40group.calendar.google.com/public/basic.ics")


# @event_source(background_color="white", text_color="#6F371F", url="http://www.meetup.com/ruby_burgers-rb", predefined_tags=["ruby", "code", "drink"])
def ruby_burgers():
    """<p>Ruby lovers meet burger lovers. Join us to talk about ruby AND burgers in the best burger places in Brussels</p>"""
    return generic_meetup("ruby_burgers-rb")


# @event_source(background_color="#99ccff", text_color="#000000", url="http://src.radiocampus.be/", key="start")
def source():
    """
    <p>L’émission Source est une émission bimensuelle sur Radio Campus Bruxelles,
    disponible à Bruxelles sur le 92.1 de la bande FM, ou partout via
    <a href="http://streamer.radiocampus.be:8000/">son flux Icecast</a>,
    si la réception est mauvaise ou impossible d'où vous êtes.</p>
    <p><a href="http://src.radiocampus.be/equipe/">L'équipe</a>
    prend les micros le vendredi à 18 heures, une semaine sur deux,
    et vous accompagne pendant une heure et demie. Le sujet de l’émission est
    principalement le Libre, que ce soit dans une perspective informatique,
    sociale ou culturelle.
    </p>
    """
    radio_campus_program = requests.get("http://emissions.radiocampus.be/horaire").content
    name = "Source"

    # 1. get all lines which are a day name or the emission name
    interesting = ("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche", name)
    is_interesting = lambda line: any(filter(lambda word: word in line, interesting))
    interesting_lines = filter(is_interesting, radio_campus_program.split('\n'))

    # 2. We ensure the first entry is today's name (don't fuck-up calendar)
    if "Aujourd'hui" not in interesting_lines[0]:
        return

    # 3. We walk the interesting lines, keepin track of the current day
    today = datetime.today()
    for line in interesting_lines[1:]:
        if name in line:
            words = map(str.strip, line.split())
            start, end = map(lambda x: map(int, x.split(':')), words[0:2])
            title = " ".join(words[2:])
            start_time = datetime(today.year, today.month, today.day, *start)
            end_time = datetime(today.year, today.month, today.day, *end)
            yield {
                'title': title,
                'start': start_time,
                'end': end_time,
                'url': "http://src.radiocampus.be/",
            }
        else:
            today += timedelta(days=1)


@event_source(background_color="#f2ab79", text_color="#000000", url="http://www.meetup.com/fr/Space-Enthusiasts-Belgium/", predefined_tags=['space'])
def space_enthusiasts_belgium():
    """
    <p>Interested in space? Whether you're just a science fiction junkie, or the next Elon Musk, everyone is welcome in this group! We do events from visiting space-related locations, to discussing books to read, to building the next rocket and satellite. All are welcome!</p>
"""
    return generic_meetup("Space-Enthusiasts-Belgium")


@event_source(background_color="#aa79f2", text_color="#000000", url="http://www.meetup.com/StreamProcessing-be/", predefined_tags=['code', 'stream_processing'])
def streamprocessing_be():
    """
    <p>A Belgium based Meetup about Stream Processing (where all data is treated as a continuous stream of (immutable) Facts, Events, Updates).</p>
    <p>A good introduction is this recent article on O'Reilly:</p>
    <p> <a class="linkified" href="http://radar.oreilly.com/2015/04/a-real-time-processing-revival.html">http://radar.oreilly.com/2015/04/a-real-tim...</a> </p>
"""
    return generic_meetup("StreamProcessing-be")


@event_source(background_color="#333333", text_color="#ffffff", url="http://www.meetup.com/Symfony-User-Group-Belgium/", predefined_tags=['code', 'php', 'symfony'])
def symfony_user_group_belgium():
    """
    <p>The Symfony User Group in Belgium, for Belgians, by Belgians. We speak about everything related to Symfony.</p>
"""
    return generic_meetup("Symfony-User-Group-Belgium")


@event_source(background_color="#82FEA9", text_color="#DC0000", url="https://www.level2.lu/", predefined_tags=["hackerspace"])
def syn2cat():
    """
    <p>L'agenda du Syn2Cat, hackerspace Luxembourgeois</p>
    """
    return generic_google_agenda("https://level2.lu/events/ical")


@event_source(background_color="#333", text_color="white", url="http://www.timelab.org")
def timelab():
    """<p>Timelab brengt makers samen. Deel uitmaken van de makers-community stimuleert leren, samenwerken, creativiteit, innovatie en experiment.</p>"""
    soup = BeautifulSoup(requests.get("http://www.timelab.org/agenda").content)

    while soup:
        for event_dom in soup('div', 'events')[0]('li', 'views-row'):
            title = event_dom('h2', 'title')[0].text
            url = event_dom('a')[0]['href']
            if not url.startswith('http'):
                url = "http://www.timelab.org" + url

            start_dom = event_dom('span', 'date-display-start')
            if start_dom:
                start = parse(start_dom[0]['content']).replace(tzinfo=None)
                end = parse(event_dom('span', 'date-display-end')[0]['content']).replace(tzinfo=None)
                all_day = False
            else:
                start_dom = event_dom('span', 'date-display-single')
                start = parse(start_dom[0]['content']).replace(tzinfo=None)
                end = None
                all_day = True

            yield {
                'title': title,
                'start': start,
                'end': end,
                'all_day': all_day,
                'url': url.replace("/nl/", ""),
                'location': "Brusselsepoortstraat 97 9000 Gent",
                'tags': ('fablab',)
            }

        next_page_links = soup('li', 'pager-next')
        if next_page_links and next_page_links[0].text:
            href = "http://www.timelab.org/" + next_page_links[0]('a')[0]['href']
            soup = BeautifulSoup(requests.get(href).content)
        else:
            soup = None


@event_source(background_color="pink", text_color="black", predefined_tags=["hackerspace"], url="http://urlab.be")
def urlab():
    """
    <p>
    UrLab est le hackerspace de l’ULB. Il s’agit d'un laboratoire ouvert par et
    pour les étudiants, où l’on met à disposition une infrastructure pour qu’ils
    puissent y exprimer leur créativité de manière collaborative.
    </p>
    """
    return json_api("https://urlab.be/api/hackeragenda.json")


@event_source(background_color="#25272C", text_color="#C58723", key=None, url="http://voidwarranties.be")
def voidwarranties():
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

    return generic_meetup("VoidWarranties")


@event_source(background_color="#7ef279", text_color="#000000", url="http://www.meetup.com/wajug-be/", predefined_tags=['code'])
def wajug_be():
    """
    <p>WAJUG est votre groupe d'utilisateurs local, Wallon, abordant "tout ce qui touche au développement logiciel". Tout ceci dans une ambiance fun, amicale, ouverte et typiquement wallonne.</p>
"""
    return generic_meetup("wajug-be")


@event_source(background_color="#F99232", text_color="white", url="http://www.meetup.com/WebRTC-crossingborders", predefined_tags=["code", "webrtc", "webdev"])
def webrtc():
    """
    <p>
    As part of a community who believe that WebRTC is a movement for the next
    years, we exchange ideas, knowledge and experience, projects on where and how
    to apply this new future focused browser-to-browser technology.<br>

    Join the enthousiasts about new technologies and business related
    opportunities.&nbsp;
    </p>
    """
    return generic_meetup("WebRTC-crossingborders")


#@event_source(background_color="white", text_color="black", url="http://www.0x20.be")
def whitespace():
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

        yield {
            'title': title,
            'url': url,
            'start': start,
            'end': end,
            'location': location.strip() if location else None,
            'tags': ('hackerspace',)
        }


# @event_source(background_color="#666661", text_color="black")
def wolfplex():
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

        yield {
            'title': title,
            'url': url,
            'start': start,
            'location': location,
            'tags': ('hackerspace',)
        }


@event_source(background_color="#3EBDEA", text_color="#000", url="https://makilab.org")
def makilab():
    "<p>Makilab est le fablab de Louvain-La-Neuve, dans le Brabant Wallon.</p>"
    soup = BeautifulSoup(requests.get("https://makilab.org/events-list").content, 'html.parser')

    while soup:
        for event in soup.find("div", "view-events-list").find("tbody"):
            # empty string, skip
            if isinstance(event, NavigableString):
                continue

            title = event.find("td", "views-field-title").a.text

            datetimeTag = event.find("td", "views-field-field-event-datetime").span
            if datetimeTag.div:
                start = parse(datetimeTag.div.find("span", "date-display-start")["content"])
                end = parse(datetimeTag.div.find("span", "date-display-end")["content"])
                all_day = False
            else:
                start = parse(datetimeTag["content"])
                end = None
                all_day = True

            urlTag = event.find("td", "views-field-view-node")
            base_domain = "https://makilab.org" if not urlTag.a["href"].startswith("http") else ""
            url = (base_domain + urlTag.a["href"]) if urlTag.a else "https://makilab.org"

            tags = ('fablab',)
            if title == "TechLab - sur RDV par email uniquement":
                tags = ('fablab', 'on_reservation')

            yield {
                'title': title,
                'start': start.replace(tzinfo=None),
                'end': end.replace(tzinfo=None) if end else end,
                'all_day': all_day,
                'url': url,
                'location': "Rue Zénobe Gramme 1348 Louvain-La-Neuve",
                'tags': tags
            }

        next_page_links = soup('li', 'pager-next')

        if next_page_links and next_page_links[0].text:
            href = "https://makilab.org/" + next_page_links[0]('a')[0]['href']
            soup = BeautifulSoup(requests.get(href).content, 'html.parser')
        else:
            soup = None


@event_source(background_color="#1ABC9C", text_color="black", predefined_tags=["hackerspace","makerspace"], url="https://ko-lab.space")
def ko_lab():
    """
    <p>A makerspace – also referred to as a hacklab. Is a community-operated workspace where people can meet, socialize and ko-laborate. Often with common interests in science, technology, articrafts, digital art etc. It offers the place and time to do or find out what you really love to do.</p>
    <p>Dus, Ko-Lab biedt de ruimte; jij bepaalt of het een werkplek, een gezellige huiskamer, een atelier, een machinewinkel, een kunststudio, een leerplek en/of een ontmoetingsplek wordt.</p>
    """
    return json_api("https://ko-lab.space/hackeragenda")

# generic_facebook("Ko-Lab", "HS.ko.lab", background_color="#1ABC9C", text_color="black", predefined_tags=["hackerspace","makerspace"], url="https://ko-lab.space")
# generic_facebook_page("HS.ko.lab")
