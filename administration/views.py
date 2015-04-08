from django.shortcuts import render

from .forms import AddEventForm


def dashboard(request):
    form = AddEventForm()
    form.for_user(request.user)

    return render(request, "administration/dashboard.haml", {
        "form": form
    })
