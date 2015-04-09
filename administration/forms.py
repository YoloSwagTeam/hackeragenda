from django import forms
from django.conf import settings

from .models import Source


class AddEventForm(forms.Form):
    title = forms.CharField()
    source = forms.ChoiceField()
    url = forms.URLField()
    start = forms.DateTimeField()
    end = forms.DateTimeField(required=False)
    all_day = forms.BooleanField()
    location = forms.CharField(required=False)

    def for_user(self, user):
        self["source"].field.choices = [(x.id, x.name) for x in Source.objects.filter(agenda=settings.AGENDA, users=user)]
