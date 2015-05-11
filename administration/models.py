from django.db import models
from django.contrib.auth.models import User

from events.models import Event


class Source(models.Model):
    name = models.CharField(max_length=255)
    border_color = models.CharField(max_length=255)
    text_color = models.CharField(max_length=255)
    agenda = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField()

    users = models.ManyToManyField(User)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        to_return = super(Source, self).save(*args, **kwargs)
        Event.objects.filter(source=self.name).update(text_color=self.text_color, border_color=self.border_color)
        return to_return
