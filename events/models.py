from django.db import models
from taggit.managers import TaggableManager


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
        if self.all_day:
            date = self.start.strftime("%Y-%m-%d")
        elif self.end:
            date = "%s - %s" % (self.start, self.end)
        else:
            date = "%s" % (self.start)

        title = self.title
        if self.location:
            title += " - %s" % (self.location)

        return u"[%s] %s (%s)" % (self.source, title, date)


class LocationCache(models.Model):
    string = models.CharField(max_length=255, db_index=True)
    lon = models.FloatField(default=None, null=True, blank=True)
    lat = models.FloatField(default=None, null=True, blank=True)

    def __unicode__(self):
        return u"%s (%s, %s)" % (self.string, self.lon, self.lat)
