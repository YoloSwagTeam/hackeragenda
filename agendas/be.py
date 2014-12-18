# encoding: utf-8

import requests
import time
import calendar

from BeautifulSoup import BeautifulSoup
from django.template.defaultfilters import slugify
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from icalendar import Calendar
from HTMLParser import HTMLParser

from events.management.commands.fetch_events import (
    event_source,
    generic_meetup, generic_eventbrite, generic_google_agenda,
    json_api
)

@event_source(background_color="#133F52", text_color="#FFFFFF", key=None, url="https://groups.google.com/d/forum/afpyro-be")
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


def agenda_du_libre_be_duplicate(event_query, detail):
    id = detail["url"].split("/")[-1].split("=")[-1]
    event_query.filter(url="http://www.agendadulibre.be/showevent.php?id=%s" % id).delete()
    event_query.filter(url="http://www.agendadulibre.be/events/%s" % id).delete()


@event_source(background_color="#3A87AD", text_color="white", url="http://www.agendadulibre.be", key=agenda_du_libre_be_duplicate)
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


generic_meetup("agile_belgium", "Agile-Belgium", background_color="#D2353A", text_color="white", description="<p>This is the meetup group of the Agile Belgium community. We organize regular drinkups and user group meetings. Come after work and meet people you usually only meet at conferences. Anyone interested in Agile or Lean can join.</p>")


generic_meetup("aws_user_group_belgium", "AWS-User-Group-Belgium", background_color="#F8981D", text_color="white", tags=["cloud", "amazon", "aws", "sysadmin"], description="<p>This is a group for anyone interested in cloud computing on the Amazon Web Services platform. All skills levels are welcome.</p>")


generic_google_agenda(
    "belgian_blender_user_group",
    "https://www.google.com/calendar/ical/7chafqnhlfkjqhp806t1tefsgc%40group.calendar.google.com/public/basic.ics",
    background_color="#F39532", text_color="white", url="http://bbug.tuxfamily.org",
    tags=["blender", "art", "3D-modeling"],
    per_event_url_function=lambda event: event["DESCRIPTION"],
    description="""
    <p>The Belgian Blender User Group is a belgium based community of users of the open source software called <a href="https://www.blender.org/">Blender</a>.</p>
    <p>We are a group of users targeting IRL meetings and organizing workshops and training.</p>
    """
)


generic_meetup("belgian_angularjs", "The-Belgian-AngularJS-Meetup-Group", background_color="#9D3532", text_color="white", tags=["angularjs", "javascript", "webdev", "programming"], description="<p>Let's get together for some discussions about the awesome AngularJS framework! I started this group to meet the belgian AngularJS community and share together our experience.</p>")


generic_meetup("belgian_nodejs_user_group", "Belgian-node-js-User-Group", background_color="#1D1D1D", text_color="white", tags=["nodejs", "javascript", "programming"], description='<p>This node.js user group gathers the belgian node.js developers so we can improve our skill set and build kick-ass amazing apps.<br><br>For the time being: find us on line at <a href="http://www.shadowmedia.be/nodejs/">http://www.shadowmedia.be/nodejs/</a>.</p>')


generic_meetup("belgian_puppet_user_group", "Belgian-Puppet-User-Group", background_color="#7B6DB0", text_color="white", tags=["puppet", "sysadmin", "devops"], description="<p>Bringing puppet loving people together on a regular base, to talk about best practices, their experience and have interesting discussions about a great configuration management tool.<br><br>IRC: freenode - #puppet-be</p>")


generic_meetup("belgian_ruby_user_group", "brug__", background_color="#E0393E", text_color="white", tags=["ruby", "programming"], description="<p>BRUG is the Belgian Ruby User Group.</p>")


generic_meetup("bescala", "BeScala", background_color="#FEE63C", text_color="#000000", tags=["java", "scala", "jvm", "programming"], description="<p>The Belgian Scala User Group.</p>")


@event_source(background_color="DarkGoldenRod", text_color="white", url="http://bhackspace.be")
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


generic_meetup("bigdata_be", "bigdatabe", background_color="black", text_color="white", tags=["bigdata", "programming", "nosql"], description="<p>Welcome to our Belgian community about bigdata, NoSQL and anything data. If you live or work in Belgium and are interested in any of these technologies, please join! We want you!</p>")


@event_source(background_color="#828282", text_color="white", key=None, url="https://blender-brussels.github.io/")
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


generic_meetup("brussels_cassandra_users", "Brussels-Cassandra-Users", background_color="#415A6C", text_color="#CBE5F7", tags=["nosql", "jvm", "database", "bruxelles", "programming"], description="<p>Open to all those interested in Apache Cassandra, Big Data, Hadoop, Hive, Hector, NoSQL, Pig, and high scalability. Let's get together and share what we know!</p>")


generic_meetup("brussels_data_science_meetup", "Brussels-Data-Science-Community-Meetup", background_color="#CAD9EC", text_color="black", tags=["bruxelles", "programming", "bigdata"], description='<p>The <strong>Blender-Brussels</strong> − also known as <strong>Blender BPY/BGE workshops</strong> − are a series of monthly work sessions organized by <a href="http://xuv.be">Julien Deswaef</a> (<a href="https://github.com/xuv" class="user-mention">@xuv</a>) and <a href="http://frankiezafe.org">François Zajéga</a> (<a href="https://github.com/frankiezafe" class="user-mention">@frankiezafe</a>) with the aim of providing a regular gathering and knowledge sharing space for artists and coders interested in Python scripting in the context of Blender.</p>')


generic_meetup("brussels_wordpress", "wp-bru", background_color="#0324C1", text_color="white", tags=["bruxelles", "wordpress", "cms", "php", "webdev"], description='<p>A gathering of WordPress users and professionals of all levels.<br><br>Whether you\'re a site owner, designer, developer, plug-in creator all are welcome to attend to learn, share and expand their knowledge of WordPress.<br><br>Have a look at <a href="http://www.meetup.com/wp-bru/about/">our about page</a> for a idea of the type of activities I\'d like to see organised.</p>')


@event_source(background_color="#FEED01", text_color="black", url="http://budalab.fikket.com")
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


@event_source(background_color="white", text_color="#990000", url="http://www.bxlug.be")
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


@event_source(background_color="#D2C7BA", text_color="black", key=None, url="http://www.constantvzw.org")
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
            elif len(data) == 5:  # data = [u'12', u'to', u'23', u'January', u'2015']
                start = parse("%s %s %s" % tuple(data[:1] + data[-2:]))
                end = parse("%s %s %s" % tuple(data[-3:]))
            elif len(data) == 7:
                start = parse("%s %s %s" % tuple(data[:3]))
                end = parse("%s %s %s" % tuple(data[4:]))
            elif len(data) == 9:  # data = [u'23', u'January', u'2015', u'21:00', u'to', u'24', u'January', u'2015', u'05:00']
                start = parse("%s %s %s %s" % tuple(data[:4]))
                end = parse("%s %s %s %s" % tuple(data[5:]))
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


generic_meetup("docker_belgium", "Docker-Belgium", background_color="#008FC4", text_color="white", tags=["docker", "lxc", "sysadmin", "devops"], description='<p>Meet other developers and ops engineers using Docker.&nbsp;Docker is an open platform for developers and sysadmins to build, ship, and run distributed applications. Consisting of Docker Engine, a portable, lightweight runtime and packaging tool, and Docker Hub, a cloud service for sharing applications and automating workflows, Docker enables apps to be quickly assembled from components and eliminates the friction between development, QA, and production environments. As a result, IT can ship faster and run the same app, unchanged, on laptops, data center VMs, and any cloud.</p><p>Learn more about Docker at&nbsp;<a href="http://www.docker.com/">http://www.docker.com</a></p>')

generic_meetup("ember_js_brussels", "Ember-js-Brussels", background_color="#FC745D", text_color="white", tags=["emberjs", "javascript", "programming", "webdev"], description="This is a group for anyone interested in developing web applications in Ember.js. I created this group because it's nice to have a local community for sharing knowledge, ideas and inspiration about this awesome web framework. The learning curve for Ember.js is not the lightest so it will also be a place to share your frustrations! Beginner or expert, everyone is welcome.")


@event_source(background_color="#C9C4BF", text_color="black", key=None, url="http://fo.am")
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


@event_source(background_color="coral", text_color="white", key=None, url="https://hackerspace.be")
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

        if "TechTue" in event["fulltext"] or "Garbage day" in event["fulltext"]:
            db_event.tags.add("meeting")

        db_event.tags.add("hackerspace")


generic_google_agenda(
    "imal",
    "https://www.google.com/calendar/ical/8kj8vqcbjk4o7dl26bvi6lm3no%40group.calendar.google.com/public/basic.ics",
    background_color="#F47D31", text_color="white", url="http://www.imal.org/fablab/",
    tags=["fablab", "art"],
    description="""
    <p>iMAL (interactive Media Art Laboratory), is a non-profit association
    created in Brussels in 1999, with the objective to support artistic forms
    and creative practices using computer and network technologies as their
    medium. In 2007, iMAL opened its new venue: a Centre for Digital Cultures
    and Technology of about 600m2 for the meeting of artistic, scientific and
    industrial innovations. A space entirely dedicated to contemporary artistic
    and cultural practices emerging from the fusion of computer,
    telecommunication, network and media.</p>
    """
)


@event_source(background_color="#296038", text_color="#6FCE91", url="http://www.incubhacker.be")
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


generic_meetup("jeudi_du_libre_mons", "Jeudis-du-Libre-Mons", background_color="#579FAB", text_color="black", tags=["mons-hainaut", "libre"], description="<p>La création des Jeudis du Libre est l’initiative de jeunes administrateurs systèmes désireux de communiquer sur Les Logiciels Libres. Tout les troisièmes jeudis du mois, un programme issu du travail de développeurs à travers le monde, est présenté aux administrateurs systèmes, aux amateurs d’informatique, aux professeurs ou encore aux simples curieux.</p>")


generic_meetup("laravel_brussels", "Laravel-Brussels", background_color="#FFFFFF", text_color="#FB503B", tags=["bruxelles", "laravel", "php", "webdev", "programming"], description='<p>A group for anyone interested in learning about and sharing knowledge on Laravel, the "PHP framework for web artisans". The group welcomes beginners and experts, amateurs and pros, young and old, etc. Laravel is an accessible, yet powerful framework for web application development. Its expressive, elegant syntax and its clean structure make PHP development a real joy. As the Laravel community keeps growing, this group is an attempt to get Belgium-based users to know each other, and to spread the word!</p>')


generic_meetup("les_mardis_de_l_agile", "Les-mardis-de-lagile-Bruxelles", background_color="#37C2F1", text_color="black", tags=["bruxelles", "agile", "programming", "drink"], description="<p>Appel à la communauté agile de Bruxelles ! Que vous soyez un fervent agiliste ou tout simplement intéressé par l'agilité, venez découvrir de nouvelles approches, vous enrichir à travers les nombreuses sessions proposées, participer à des innovation games et partager vos retours d'expérience lors de nos meetups \"Les Mardis de l'agile\" !</p>")


generic_meetup("mongodb_belgium", "MongoDB-Belgium", background_color="#3EA86F", text_color="white", tags=["mongodb", "database", "programming"], description="<p>The first countrywide MongoDB user group in Belgium. Meetups will be held every 3 months. Talk proposals can be sent to hannes@showpad.com.</p>")


@event_source(background_color="DarkBlue", text_color="white", url="http://neutrinet.be")
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


generic_google_agenda(
    "okfnbe",
    "https://www.google.com/calendar/ical/sv07fu4vrit3l8nb0jlo8v7n80@group.calendar.google.com/public/basic.ics",
    background_color="#299C8F", text_color="white", url="https://www.google.com",
    tags=["opendata"],
    description="""
    <p>Open Knowledge Belgium is a not for profit organisation (vzw/asbl) ran
    by a board of 6 people and has currently 1 employee. It is an umbrella
    organisation for Open Knowledge in Belgium and, as mentioned below, contains
    different working groups of people working around various projects.</p>

    <p>If you would like to have your activities under our wing, please contact us at our mailinglist.</p>
    """
)


@event_source(background_color="#FFFFFF", text_color="#00AA00", url="http://www.okno.be")
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


def opengarage_duplicated(event_query, detail):
    events = [event for event in event_query.all() if not event.url.split("/")[-2].isdigit()]
    map(lambda x: x.delete(), events)


def opengarage_meetings(event):
    if event.title == "Open Garage":
        event.tags.add("meeting")


generic_meetup("opengarage", "OpenGarage", background_color="DarkOrchid", text_color="white", tags=["hackerspace", opengarage_meetings], description='''<p>The "Open Garage" is a double garage in Borsbeek, Belgium, some sort of <a href="http://en.wikipedia.org/wiki/Hackerspace">hackerspace</a>, where I (<a href="https://plus.google.com/u/2/+AnthonyLiekens/posts">Anthony Liekens</a>) host weekly workshops and many of my projects. The garage is open every Thursday evening to everyone who wants to join our community\'s numerous hacking projects.</p>
<p>Don\'t listen to me, but check out the media\'s reviews of the Open Garage:</p>
<ul>
<li><a href="http://hackaday.com/2013/10/22/hackerspacing-in-europe-garage-space-in-antwerp/">Hackaday\'s review of the Open Garage</a></li>
<li><a href="http://anthony.liekens.net/pub/gva20140614.pdf">The Open Garage in GvA\'s Citta</a> (Belgian newspaper)</li>
<li><a href="https://www.youtube.com/watch?v=aCuUv5ltw6g">The Open Garage in "Iedereen Beroemd"</a> (Belgian national TV)</li>
<li><a href="http://www.radio1.be/programmas/de-bende-van-einstein/binnenkijken-de-garage-van-anthony-liekens">The Open Garage on Radio 1</a> (Belgian national radio)</li>
<li><a href="http://krant.tijd.be/ipaper/20140215#paper/sabato_nl/50">The Open Garage in De Tijd</a> (Belgian "Times" newspaper)</li>
</ul>''', key=opengarage_duplicated)


generic_meetup("opentechschool", "OpenTechSchool-Brussels", background_color="#3987CB", text_color="white", tags=["learning", "programming", "bruxelles"], description='''
<p>OpenTechSchool is a community initiative offering free programming workshops
and meetups to technology enthusiasts of all genders, backgrounds, and
experience levels. It supports volunteer coaches in setting up events by taking
care of the organizational details, encouraging coaches to create original
teaching material.</p>
<p>Everyone is invited to participate, whether as a coach or a learner in this
friendly learning environment where no one feels shy about asking any
questions.</p>
<p><a href="http://www.opentechschool.org/" class="linkified">http://www.opentechschool.org/</a></p>''')


generic_eventbrite("owaspbe", "owasp-belgium-chapter-1865700117", background_color="#4366AF", text_color="white", tags=["security"], description='''
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


generic_meetup("phpbenelux", "phpbenelux", background_color="#015074", text_color="white", tags=["php", "programming", "webdev"], description="<p>PHPBenelux user group meetings are a fun way to learn about best practices and new innovations from the world of PHP and to hang out with other PHP developers</p>")

generic_eventbrite("realize", "realize-6130306851", background_color="#36c0cb", text_color="black", tags=["makerspace", "bruxelles"], description="""
<p><strong>Realize</strong> est un atelier partagé<a title="plan" href="https://www.google.be/maps/preview#!q=Rue+du+M%C3%A9tal+32%2C+Saint-Gilles&amp;data=!4m10!1m9!4m8!1m3!1d23940!2d4.802835!3d50.988438!3m2!1i1920!2i912!4f13.1" target="_blank"> situé à Saint-Gilles</a>, à deux pas du Parvis. Tous ceux qui veulent réaliser des objets peuvent y accéder grâce à diverses <a href="http://realizebxl.be/inscription/">formules d’abonnement</a>.</p>
""", url="http://realizebxl.be/")


generic_google_agenda(
    "relab",
    "https://www.google.com/calendar/ical/utmnk71g19dcs2d0f88q3hf528%40group.calendar.google.com/public/basic.ics",
    background_color="#2BC884", text_color="white", url="http://www.relab.be",
    tags=["fablab"],
    description="""
    <p><strong>Le RElab, premier Fab Lab de Wallonie, est un atelier numérique ouvert au public et une structure de développement créatif local.</strong>
    La spécificité du RElab réside dans l’utilisation de matériaux de récupération comme matière première et dans l’étude de nouveaux procédés sociaux,
    créatifs et économiques d’upcycling, en liaison avec les nouveaux moyens&nbsp;de fabrication et de communication numérique.</p>
    """
)


generic_meetup("ruby_burgers", "ruby_burgers-rb", background_color="white", text_color="#6F371F", tags=["ruby", "programming", "drink"], description="<p>Ruby lovers meet burger lovers. Join us to talk about ruby AND burgers in the best burger places in Brussels</p>")


@event_source(background_color="#99ccff", text_color="#000000", url="http://src.radiocampus.be/", key="start")
def source(create_event):
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
            create_event(title=title, start=start_time, end=end_time, url="http://src.radiocampus.be/")
        else:
            today += timedelta(days=1)


@event_source(background_color="#82FEA9", text_color="#DC0000", url="https://www.hackerspace.lu/")
def syn2cat(create_event):
    "<p>L'agenda du Syn2Cat, hackerspace Luxembourgeois</p>"

    data = Calendar.from_ical(requests.get("https://wiki.hackerspace.lu/wiki/Special:Ask/-5B-5BCategory:Event-5D-5D-20-5B-5BStartDate::%2B-5D-5D-20-5B-5BStartDate::-3E2014-2D06-2D30-5D-5D/-3FStartDate%3Dstart/-3FEndDate%3Dend/-3FHas-20location/-5B-5BCategory:Event-5D-5D-20-5B-5BStartDate::%2B-5D-5D-20-5B-5BStartDate::-3E2014-2D06-2D30-5D-5D/-3FStartDate%3Dstart/-3FEndDate%3Dend/-3FHas-20location/mainlabel%3D/limit%3D50/order%3DASC/sort%3DStartDate/format%3Dicalendar").content)

    for event in data.walk()[1:]:
        db_event = create_event(
            title=event["SUMMARY"].encode("Utf-8"),
            start=event["DTSTART"].dt.replace(tzinfo=None) if isinstance(event["DTSTART"].dt, datetime) else event["DTSTART"].dt,
            end=event["DTEND"].dt.replace(tzinfo=None) if isinstance(event["DTEND"].dt, datetime) else event["DTEND"].dt,
            url=event["URL"],
        )

        db_event.tags.add("hackerspace", "luxembourg")

        if "openmonday" in db_event.title.lower():
            db_event.tags.add("meeting")


@event_source(background_color="#333", text_color="white", url="http://www.timelab.org")
def timelab(create_event):
    """<p>Timelab brengt makers samen. Deel uitmaken van de makers-community stimuleert leren, samenwerken, creativiteit, innovatie en experiment.</p>"""
    soup = BeautifulSoup(requests.get("http://www.timelab.org/nl/agenda").content)

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

            create_event(
                title=title,
                start=start,
                end=end,
                all_day=all_day,
                url=url
            ).tags.add("fablab")

        next_page_links = soup('li', 'pager-next')
        if next_page_links and next_page_links[0].text:
            href = "http://www.timelab.org" + next_page_links[0]('a')[0]['href']
            soup = BeautifulSoup(requests.get(href).content)
        else:
            soup = None


json_api("urlab", "https://urlab.be/hackeragenda.json", background_color="pink", text_color="black", tags=["hackerspace"], description="""
<p>
UrLab est le hackerspace de l’ULB. Il s’agit d'un laboratoire ouvert par et
pour les étudiants, où l’on met à disposition une infrastructure pour qu’ils
puissent y exprimer leur créativité de manière collaborative.
</p>
""", source_url="http://urlab.be")


@event_source(background_color="#25272C", text_color="#C58723", key=None, url="http://voidwarranties.be")
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


generic_meetup("webrtc", "WebRTC-crossingborders", background_color="#F99232", text_color="white", tags=["programming", "webrtc", "webdev"], description="""
<p>
As part of a community who believe that WebRTC is a movement for the next
years, we exchange ideas, knowledge and experience, projects on where and how
to apply this new future focused browser-to-browser technology.<br>

Join the enthousiasts about new technologies and business related
opportunities.&nbsp;
</p>
""")


@event_source(background_color="white", text_color="black", url="http://www.0x20.be")
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

