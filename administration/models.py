from django.db import models
from django.contrib.auth.models import User


class Source(models.Model):
    name = models.CharField(max_length=255)
    border_color = models.CharField(max_length=255)
    text_color = models.CharField(max_length=255)
    agenda = models.CharField(max_length=255)

    users = models.ManyToManyField(User)

    def __unicode__(self):
        return self.name
