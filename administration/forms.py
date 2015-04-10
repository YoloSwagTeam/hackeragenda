from django import forms
from django.conf import settings

from .models import Source


class AddEventForm(forms.Form):
    title = forms.CharField()
    source = forms.ModelChoiceField(queryset=Source.objects.all(), empty_label=None)
    url = forms.URLField()
    start = forms.DateTimeField()
    end = forms.DateTimeField(required=False)
    all_day = forms.BooleanField(required=False)
    location = forms.CharField(required=False)

    def for_user(self, user):
        self["source"].field.queryset = Source.objects.filter(agenda=settings.AGENDA, users=user)
