from django.db import models
from taggit.managers import TaggableManager
from datetime import date
from .color import add_alpha


class Event(models.Model):
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    color = models.CharField(max_length=255, null=True, blank=True)
    text_color = models.CharField(max_length=255, null=True, blank=True)
    border_color = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    all_day = models.BooleanField(null=False, blank=True, default=False)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    agenda = models.CharField(max_length=255)
    tags = TaggableManager()

    lon = models.FloatField(default=None, null=True, blank=True)
    lat = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        title = self.title
        if self.location:
            title += " - %s" % (self.location)
        return f"[{self.source}] {title} ({self.date_to_string})"

    @property
    def date_to_string(self):
        if self.all_day:
            if self.end and self.end != self.start:
                res = "%s - %s" % tuple(x.strftime("%Y-%m-%d") for x in (self.start, self.end))
            else:
                res = self.start.strftime("%Y-%m-%d")
        elif self.end:
            res = "%s - %s" % (self.start, self.end)
        else:
            res = "%s" % (self.start)
        return res

    @property
    def is_over(self):
        when = self.end if self.end else self.start
        return when.date() < date.today()

    @property
    def calendar_border_color(self):
        color = self.border_color
        return add_alpha(color, .7) if self.is_over else color

    @property
    def calendar_text_color(self):
        color = self.text_color
        return add_alpha(color, .5) if self.is_over else color

    class Meta:
        ordering = ['start']


class LocationCache(models.Model):
    string = models.CharField(max_length=255, db_index=True, unique=True)
    lon = models.FloatField(default=None, null=True, blank=True)
    lat = models.FloatField(default=None, null=True, blank=True)

    def __unicode__(self):
        return f"{self.string} ({self.lon}, {self.lat})"
