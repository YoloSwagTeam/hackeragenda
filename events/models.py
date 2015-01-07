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

    def __unicode__(self):
        title = self.title
        if self.location:
            title += " - %s" % (self.location)
        return u"[%s] %s (%s)" % (self.source, title, self.datestr)

    @property
    def datestr(self):
        if self.all_day:
            return self.start.strftime("%Y-%m-%d")
        elif self.end:
            return "%s - %s" % (self.start, self.end)
        else:
            return "%s" % (self.start)

    @property
    def is_over(self):
        when = self.end if self.end else self.start
        return when.date() < date.today()

    @property
    def calendar_colors(self):
        border, text = self.border_color, self.text_color
        if self.is_over:
            border, text = add_alpha(border, .7), add_alpha(text, .7)
        return {"color": border, "textColor": text}

class LocationCache(models.Model):
    string = models.CharField(max_length=255, db_index=True, unique=True)
    lon = models.FloatField(default=None, null=True, blank=True)
    lat = models.FloatField(default=None, null=True, blank=True)

    def __unicode__(self):
        return u"%s (%s, %s)" % (self.string, self.lon, self.lat)
