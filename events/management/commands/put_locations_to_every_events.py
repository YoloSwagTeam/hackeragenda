import os
import re
import time
import json

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from django.core.management.base import BaseCommand
from events.models import Event


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        caching = {}
        fails = json.load(open("/tmp/hackeragenda_geopy_fails.json", "r")) if os.path.exists("/tmp/fails.json") else []

        geolocator = Nominatim()
        for i in filter(lambda x: x.location.strip(), Event.objects.filter(location__isnull=False, lon__isnull=True, lat__isnull=True)):
            if i.location in fails:
                continue

            print i.title, "----", i.location, [i.lon], [i.lat]

            if i.location in caching:
                location = caching[i.location]
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

            caching[i.location] = location

            if location is None:
                fails.append(i.location)

                with open("/tmp/hackeragenda_geopy_fails.json", "w") as save_fails:
                    save_fails.write(json.dumps(fails, indent=4))

                print "fail, continue"
                continue


            i.lon = location.longitude
            i.lat = location.latitude
            i.save()
