import re

from django.core.management.base import BaseCommand
from datetime import date, timedelta
from events.models import Event


def tweet_size(tweet):
    return len(re.sub("https://\S*", "X"*23, re.sub("http://\S*", "X"*22, tweet)))


class Command(BaseCommand):
    def handle(self, *args, **options):
        today_events = Event.objects.filter(start__gte=date.today()).filter(start__lt=date.today() + timedelta(days=1))
        this_week_other_events = Event.objects.filter(start__gte=date.today() + timedelta(days=1)).filter(start__lt=date.today() + timedelta(days=7))

        for tweet in self.generate_tweets(today_events):
            print tweet

        if date.today().weekday() == 0:
            for tweet in self.generate_tweets(this_week_other_events):
                print tweet

    def generate_tweets(self, events):
        def format_title(x):
            return "\"%(title)s\" %(date)s%(time)s" % {
                "date": x.start.strftime("%A") if x.start.date() != date.today() else "today",
                "time": (" at %s" % x.start.strftime("%H:%M")) if not x.all_day and (x.start.hour != 0 or x.start.minute != 0) else "",
                "title": x.title
            }

        for event in events:
            tweet = [format_title(event), event.url, "#" + "".join(event.source.replace("_", " ").title().split())]
            if tweet_size(" ".join(tweet)) > 141:
                to_remove = tweet_size(" ".join(tweet)) - 140
                title = event.title[to_remove:]
                tweet[0] = format_title(event)

            tweet = " ".join(tweet)
            yield tweet
