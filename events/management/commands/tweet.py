import re
import sys
import time
import tweepy

from datetime import date, timedelta
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from events.models import Event


def tweet_size(tweet):
    return len(re.sub("https://\S*", "X"*23, re.sub("http://\S*", "X"*22, tweet)))


def connect_to_twitter():
    if not hasattr(settings, "TWITTER_ACCESS_TOKEN") or not hasattr(settings, "TWITTER_ACCESS_SECRET"):
        print "Error: TWITTER_ACCESS_TOKEN and TWITTER_ACCESS_SECRET must be set in the settings.py"
        sys.exit(1)

    auth = tweepy.OAuthHandler("KwayVtavdRYPKmnSuZO2w", "vvhA31BhosJdcpjmQJk8ORqp7M0whIDBlIAGqwAQ")
    auth.set_access_token(settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_SECRET)
    return tweepy.API(auth)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
       make_option('--run',
            action='store_true',
            dest='run',
            default=False,
            help='Actually tweet'),
    )

    def handle(self, *args, **options):
        if not options["run"]:
            print "Warning: won't tweet, use --run to actually tweet."
        else:
            self.twitter = connect_to_twitter()

        for tweet in self.generate_tweets():
            if not options["run"]:
                print tweet
            else:
                self.tweet(tweet)

    def tweet(self, t):
        print "Tweet:", t
        self.twitter.update_status(t)
        time.sleep(10)

    def generate_tweets(self):
        today_events = Event.objects.filter(agenda=settings.AGENDA).filter(start__gte=date.today()).filter(start__lt=date.today() + timedelta(days=1))
        this_week_other_events = Event.objects.filter(agenda=settings.AGENDA).filter(start__gte=date.today() + timedelta(days=1)).filter(start__lt=date.today() + timedelta(days=7))

        for tweet in self.format_tweets(today_events):
            yield tweet.encode("Utf-8")

        if date.today().weekday() == 0:
            for tweet in self.format_tweets(this_week_other_events):
                yield tweet.encode("Utf-8")

    def format_tweets(self, events):
        def format_title(x):
            return "\"%(title)s\" %(date)s%(time)s" % {
                "date": ("this %s" % x.start.strftime("%A")) if x.start.date() != date.today() else "today",
                "time": (" at %s" % x.start.strftime("%H:%M")) if not x.all_day and (x.start.hour != 0 or x.start.minute != 0) else "",
                "title": x.title
            }

        for event in events:
            tweet = [format_title(event), event.url, "#" + "".join(event.source.replace("_", " ").title().split())]
            if tweet_size(" ".join(tweet)) > 141:
                to_remove = tweet_size(" ".join(tweet)) - 140
                title = event.title[to_remove + 3:] + "..."
                tweet[0] = format_title(event)

            tweet = " ".join(tweet)
            yield tweet
