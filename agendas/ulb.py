# encoding: utf-8

import re
import requests
import time
import calendar

from bs4 import BeautifulSoup
from django.template.defaultfilters import slugify
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from icalendar import Calendar
from HTMLParser import HTMLParser

from events.management.commands.fetch_events import (
    event_source,
    generic_meetup, generic_eventbrite, generic_google_agenda,
    generic_facebook_page, generic_facebook_group, json_api
)

generic_facebook_group("agro", "5217419333", 
    background_color="#00a614", text_color="white", tags=["cercle"], 
    description="""
    <p>Arrivés il y a entre 1 et 6 ans dans cette université, baptisés ou non, nous sommes comme vous de simples étudiants voulant réussir nos études de BioIngénieurs, mais sans oublier pour autant qu'il faut savoir faire la fête et se détendre de temps en temps.... voir souvent!</p>
    """
)

generic_google_agenda(
    "cercle_informatique",
    "https://www.google.com/calendar/ical/b6s2tn7vm5mr8cl4sdq1m9qp0o%40group.calendar.google.com/public/basic.ics",
    background_color="#8a116d", text_color="white", url="http://cerkinfo.be/",
    tags=["cercle"],
    per_event_url_function=lambda event: event["DESCRIPTION"],
    description="""
    <p>Le Cercle Informatique a pour but d’aider les étudiants d'informatique - aussi bien les nouveaux que les anciens - à réussir leurs études, mais aussi à faciliter leur intégration dans la vie universitaire en essayant que celle-ci leur soit enrichissante et inoubliable. Le CI tente de mener à bien cette mission par l’organisation de divers activités festives ou non</p>
    """
)

json_api("urlab", "https://urlab.be/hackeragenda.json", 
    background_color="pink", text_color="black", tags=["hackerspace"], 
    description="""
    <p>
    UrLab est le hackerspace de l’ULB. Il s’agit d'un laboratoire ouvert par et
    pour les étudiants, où l’on met à disposition une infrastructure pour qu’ils
    puissent y exprimer leur créativité de manière collaborative.
    </p>
    """, 
    source_url="http://urlab.be"
)
