# encoding: utf-8

# import re
# import requests
# import time
# import calendar
#
# from bs4 import BeautifulSoup
# from django.template.defaultfilters import slugify
# from datetime import date, datetime, timedelta
# from dateutil.parser import parse
# from icalendar import Calendar
# from HTMLParser import HTMLParser
#
# from events.management.commands.fetch_events import event_source
# from events.generics import (
#     generic_meetup, generic_eventbrite, generic_google_agenda,
#     generic_facebook_page, generic_facebook_group, json_api
# )
#
# @event_source(background_color="#00a614", text_color="white", predefined_tags=["cercle"], url="")
# def agro():
#     """
#     <p>Arrivés il y a entre 1 et 6 ans dans cette université, baptisés ou non,
#     nous sommes comme vous de simples étudiants voulant réussir nos études de
#     BioIngénieurs, mais sans oublier pour autant qu'il faut savoir faire la fête
#     et se détendre de temps en temps.... voir souvent!</p>
#     """
#     return generic_facebook_group("5217419333")
#
#
# @event_source(background_color="#32e5da", text_color="white", predefined_tags=["cercle"], url="")
# def CGeo():
#     """<p>Cercle de Géographie et de Géologie</p>"""
#     return generic_facebook_group("148882266650")
#
#
# @event_source(
#     background_color="#4b5054", text_color="white",
#     url="http://www.chaa.be/", predefined_tags=["cercle"],
#     description=u"""<p>Cercle d'Histoire de l'Art et d'Archéologie</p>""")
# def chaa():
#     return generic_google_agenda(
#         "https://www.google.com/calendar/ical/chaa.ulb%40gmail.com/public/basic.ics",
#         per_event_url_function=lambda event: event["DESCRIPTION"])
#
#
# @event_source(background_color="#8a116d", text_color="white", url="http://cerkinfo.be/", predefined_tags=["cercle"])
# def ci():
#     """
#     <p>Le Cercle Informatique a pour but d’aider les étudiants d'informatique -
#     aussi bien les nouveaux que les anciens - à réussir leurs études, mais
#     aussi à faciliter leur intégration dans la vie universitaire en essayant
#     que celle-ci leur soit enrichissante et inoubliable. Le CI tente de mener
#     à bien cette mission par l’organisation de divers activités festives ou non
#     </p>
#     """
#     return generic_google_agenda(
#         "https://www.google.com/calendar/ical/b6s2tn7vm5mr8cl4sdq1m9qp0o%40group.calendar.google.com/public/basic.ics",
#         per_event_url_function=lambda event: event["DESCRIPTION"])
#
#
# @event_source(background_color="pink", text_color="black", predefined_tags=["hackerspace"],  url="http://urlab.be")
# def urlab():
#     """
#     <p>
#     UrLab est le hackerspace de l’ULB. Il s’agit d'un laboratoire ouvert par et
#     pour les étudiants, où l’on met à disposition une infrastructure pour qu’ils
#     puissent y exprimer leur créativité de manière collaborative.
#     </p>
#     """
#     return json_api("https://urlab.be/hackeragenda.json")
