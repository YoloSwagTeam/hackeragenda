from django import forms
from django.conf import settings

from .models import Source


input_formats = list(forms.DateTimeField.input_formats) + [
    '%Y/%m/%d %H:%M:%S',
    '%Y/%m/%d %H:%M',
    '%Y/%m/%d %Hh%M',
    '%Y/%m/%d %Hh',
    '%Y/%m/%d',
]

class AddEventForm(forms.Form):
    title = forms.CharField()
    source = forms.ModelChoiceField(queryset=Source.objects.all(), empty_label=None)
    url = forms.URLField()
    start = forms.DateTimeField(input_formats=input_formats)
    end = forms.DateTimeField(required=False, input_formats=input_formats)
    all_day = forms.BooleanField(required=False)
    location = forms.CharField(required=False)

    def for_user(self, user):
        self["source"].field.queryset = Source.objects.filter(agenda=settings.AGENDA, users=user)
