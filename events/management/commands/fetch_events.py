# encoding: utf-8

import traceback

from datetime import datetime
from collections import OrderedDict

from django.core.management.base import BaseCommand
from django.db import transaction
from events.models import Event

from importlib import import_module
from os import listdir


SOURCES_FUNCTIONS = OrderedDict()
SOURCES_OPTIONS = {}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--quiet',
            action='store_true',
            dest='quiet',
            default=False,
            help='No debug output'
        )

        parser.add_argument(
            '--nocolor',
            action='store_true',
            dest='nocolor',
            default=False,
            help='No ANSI colors in output'
        )

        parser.add_argument(
            '--strict',
            action='store_true',
            dest='strict',
            default=False,
            help='Failed on error (used for development)'
        )

    def handle(self, *args, **options):
        sources = SOURCES_FUNCTIONS.keys() if not args else args

        for source in sources:
            try:
                with transaction.atomic():
                    SOURCES_FUNCTIONS[source](
                        options.get('quiet', True),
                        options.get('nocolor', True)
                    )

            except Exception as e:
                if options.get('nocolor', True):
                    print("Error while working on '%s': %s" % (source, e))
                else:
                    print("\033[31;1m[ERROR]\033[0m While working on '\033[33;1m%s\033[0m': %s" % (source, e))
                traceback.print_exc()

                try:
                    from raven.contrib.django.raven_compat.models import client
                    client.captureException()
                except ImportError:
                    print("No Sentry")

                if options.get('strict', False):
                    raise e


def event_source(background_color, text_color, url, agenda=None, key="url", description="", predefined_tags=[]):
    if agenda is None:
        agenda = CURRENT_AGENDA

    def event_source_wrapper(func, org_name=None):
        def fetch_events(quiet, nocolor):
            def create_event(**detail):
                tags = set(predefined_tags)
                if 'tags' in detail:
                    tags = tags | set(detail.pop("tags"))

                if callable(key):
                    key(event_query=Event.objects.filter(source=org_name), detail=detail)

                elif key not in (None, False) and Event.objects.filter(**{key: detail[key]}):
                    Event.objects.filter(**{key: detail[key]}).delete()

                res = Event.objects.create(source=org_name, text_color=SOURCES_OPTIONS[org_name]["fg"], border_color=SOURCES_OPTIONS[org_name]["bg"], agenda=agenda, **detail)

                for tag in tags:
                    if callable(tag):
                        for dynamic_tag in tag(res):
                            res.tags.add(dynamic_tag)
                    else:
                        res.tags.add(tag)

                if not quiet:
                    if nocolor:
                        print(res)
                    else:
                        print(f"\033[32;1m * \033[0m{res}")

                return res

            if key in (None, False):
                Event.objects.filter(source=org_name).delete()
            else:
                Event.objects.filter(source=org_name, start__gte=datetime.now())
                Event.objects.filter(source=org_name).update(border_color=SOURCES_OPTIONS[org_name]["bg"], text_color=SOURCES_OPTIONS[org_name]["fg"])

            for event in func():
                create_event(**event)

            if not quiet:
                if nocolor:
                    print(" === Finished for", org_name)
                else:
                    print("\033[34;1m === \033[0m Finished for", org_name)

        if org_name is None:
            org_name = func.__name__.lower()

        SOURCES_OPTIONS[org_name] = {"bg": background_color, "fg": text_color, "agenda": agenda, "description": func.__doc__ if not description and func.__doc__ else description, "url": url}

        SOURCES_FUNCTIONS[org_name] = fetch_events

        return func

    return event_source_wrapper

CURRENT_AGENDA = None


def load_agenda(name):
    global CURRENT_AGENDA
    CURRENT_AGENDA = name
    try:
        import_module(f"agendas.{name}")
    except Exception as err:
        print(" === Error when loading fetchers for agenda", name)
        traceback.print_exc()
        print(err)


def load_agendas():
    for f in listdir("agendas"):
        if f == "__init__.py" or f.split(".")[-1] != 'py':
            continue
        load_agenda(f[:-3])


load_agendas()
