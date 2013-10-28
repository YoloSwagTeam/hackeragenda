from django.db import models
from events.colors import COLORS

class Event(models.Model):
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    color = models.CharField(max_length=255, null=True, blank=True)
    text_color = models.CharField(max_length=255, null=True, blank=True)
    border_color = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    all_day = models.BooleanField(null=False, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "%s [%s]" % (self.title, self.source)

    @property
    def background_color(self):
        if self.source in COLORS:
            return COLORS[self.source]['bg']
        return None

    @property
    def text_color(self):
        if self.source in COLORS:
            return COLORS[self.source]['fg']
        return None
