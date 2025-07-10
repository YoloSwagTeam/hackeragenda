from datetime import datetime

from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404

from events.models import Event

from .models import Source
from .forms import AddEventForm


def dashboard(request):
    if request.method == "GET":
        form = AddEventForm()
        form.for_user(request.user)

        sources = Source.objects.filter(users=request.user, agenda=settings.AGENDA)

        return render(
            request,
            "administration/dashboard.haml",
            {
                "form": form,
                "sources": sources,
                "next_events": Event.objects.filter(
                    source__in=[x.name for x in sources], start__gte=datetime.now()
                ).order_by("start"),
                "previous_events": Event.objects.filter(
                    source__in=[x.name for x in sources], start__lt=datetime.now()
                ).order_by("-start"),
            },
        )

    elif request.method == "POST":
        form = AddEventForm(request.POST)
        form.for_user(request.user)

        if not form.is_valid():
            sources = Source.objects.filter(users=request.user, agenda=settings.AGENDA)

            return render(
                request,
                "administration/dashboard.haml",
                {
                    "form": form,
                    "sources": sources,
                    "next_events": Event.objects.filter(
                        source__in=[x.name for x in sources], start__gte=datetime.now()
                    ).order_by("start"),
                    "previous_events": Event.objects.filter(
                        source__in=[x.name for x in sources], start__lt=datetime.now()
                    ).order_by("-start"),
                },
            )

        Event.objects.create(
            title=form.cleaned_data["title"],
            source=form.cleaned_data["source"].name,
            url=form.cleaned_data["url"],
            start=form.cleaned_data["start"],
            end=form.cleaned_data["end"],
            all_day=form.cleaned_data["all_day"],
            location=form.cleaned_data["location"],
            agenda=settings.AGENDA,
            text_color=form.cleaned_data["source"].text_color,
            border_color=form.cleaned_data["source"].border_color,
        )

        return HttpResponseRedirect(reverse("administration_dashboard"))

    else:
        raise Exception()  # XXX lazy


def update_event(request, pk):
    if request.method == "GET":
        event = get_object_or_404(Event, pk=pk)

        form = AddEventForm(
            {
                "title": event.title,
                "url": event.url,
                "source": Source.objects.get(name=event.source),
                "start": event.start,
                "end": event.end,
                "all_day": event.all_day,
                "location": event.location,
            }
        )

        form.for_user(request.user)

        return render(
            request,
            "administration/event_form.haml",
            {"form": form, "object": event, "event": event},
        )
    elif request.method == "POST":
        event = get_object_or_404(Event, pk=pk)

        form = AddEventForm(request.POST)
        form.for_user(request.user)

        if not form.is_valid():
            print(form.errors)

            return render(
                request,
                "administration/event_form.haml",
                {"form": form, "object": event, "event": event},
            )

        event.title = form.cleaned_data["title"]
        event.source = form.cleaned_data["source"].name
        event.url = form.cleaned_data["url"]
        event.start = form.cleaned_data["start"]
        event.end = form.cleaned_data["end"]
        event.all_day = form.cleaned_data["all_day"]
        event.location = form.cleaned_data["location"]

        event.save()

        return HttpResponseRedirect(reverse_lazy("administration_dashboard"))

    else:
        raise Exception()  # XXX lazy
