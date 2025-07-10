import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = "<poll_id poll_id ...>"
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        os.system(
            "curl http://hackeragenda.be/events/location_cache.yaml > events/fixtures/location_cache.yaml"
        )
