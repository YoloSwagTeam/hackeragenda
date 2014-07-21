"""
A set of predefined useful imports for events fetchers
"""

from events.management.commands.fetch_events import (
	event_source, 
	generic_meetup, generic_eventbrite, generic_facebook,
	json_api
)

import requests
import time
import calendar
import feedparser

from BeautifulSoup import BeautifulSoup
from django.template.defaultfilters import slugify
from datetime import date, datetime, timedelta
from dateutil.parser import parse
from icalendar import Calendar
from icalendar import Event as icalendarEvent
from HTMLParser import HTMLParser
