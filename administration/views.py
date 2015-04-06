from django.shortcuts import render


def dashboard(request):
    return render(request, "administration/dashboard.haml", {})
