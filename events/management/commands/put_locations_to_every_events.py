import re
import time

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from django.core.management.base import BaseCommand
from events.models import Event, LocationCache


class Command(BaseCommand):
    def handle(self, *args, **options):
        geolocator = Nominatim()

        for i in filter(lambda x: x.location.strip(), Event.objects.filter(location__isnull=False, lon__isnull=True, lat__isnull=True)):
            print i.title, "----", i.location, [i.lon], [i.lat]

            if LocationCache.objects.filter(string=i.location).exists():
                location = LocationCache.objects.get(string=i.location)
            else:
                time.sleep(5)
                try:
                    location = geolocator.geocode(i.location)
                except GeocoderTimedOut:
                    location = None

                if location is None and re.search("\(.*\)", i.location):
                    print "fail, try to look for:", re.search("(\(.+\))", i.location).group()[1:-1]
                    time.sleep(5)
                    try:
                        location = geolocator.geocode(re.search("(\(.+\))", i.location).group()[1:-1])
                    except GeocoderTimedOut:
                        location = None

                location = LocationCache.objects.create(
                    string=i.location,
                    lat=location.latitude if location else None,
                    lon=location.longitude if location else None,
                )

                if (location.lat, location.lon) == (None, None):
                    print "fail"
                    continue

            i.lon = location.lon
            i.lat = location.lat
            i.save()
