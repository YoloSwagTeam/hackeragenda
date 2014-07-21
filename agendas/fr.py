# encoding: utf-8

import requests
import calendar
import feedparser

from datetime import datetime
from BeautifulSoup import BeautifulSoup
from dateutil.parser import parse
from icalendar import Calendar

from events.management.commands.fetch_events import event_source, french_month_to_english_month

# @event_source(background_color="#3A87AD", text_color="white")
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




@event_source(background_color="#005184", text_color="white", url="https//www.april.org")
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


@event_source(background_color="#2C2C29", text_color="#89DD00", url="http://www.electrolab.fr")
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


@event_source(background_color="white", text_color="#B92037", key=None, url="http://www.pingbase.net")
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
