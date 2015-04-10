from datetime import datetime

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.conf import settings

from events.models import Event

from .models import Source
from .forms import AddEventForm


def dashboard(request):
    form = AddEventForm()
    form.for_user(request.user)

    sources = Source.objects.filter(users=request.user, agenda=settings.AGENDA)

    return render(request, "administration/dashboard.haml", {
        "form": form,
        "sources": sources,
        "next_events": Event.objects.filter(source__in=[x.name for x in sources], start__gte=datetime.now()).order_by("start"),
        "previous_events": Event.objects.filter(source__in=[x.name for x in sources], start__lt=datetime.now()).order_by("-start"),
    })


def add_event(request):
    form = AddEventForm(request.POST)
    form.for_user(request.user)

    if not form.is_valid():
        sources = Source.objects.filter(users=request.user, agenda=settings.AGENDA)

        return render(request, "administration/dashboard.haml", {
            "form": form,
            "sources": sources,
            "next_events": Event.objects.filter(source__in=[x.name for x in sources], start__gte=datetime.now()).order_by("start"),
            "previous_events": Event.objects.filter(source__in=[x.name for x in sources], start__lt=datetime.now()).order_by("-start"),
        })

    Event.objects.create(
        title=form.cleaned_data["title"],
        source=form.cleaned_data["source"],
        url=form.cleaned_data["url"],
        start=form.cleaned_data["start"],
        end=form.cleaned_data["end"],
        all_day=form.cleaned_data["all_day"],
        location=form.cleaned_data["location"],
        agenda=settings.AGENDA,
    )

    return HttpResponseRedirect(reverse("administration_dashboard"))
