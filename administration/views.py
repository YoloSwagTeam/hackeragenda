from django.shortcuts import render

from .forms import AddEventForm


def dashboard(request):
    return render(request, "administration/dashboard.haml", {
        "form": AddEventForm()
    })
