from django.db import models
from django.contrib.auth.models import User


class UserSource(models.Model):
    source = models.CharField(max_length=255)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "%s - %s" % (self.user, self.source)


class UserAgenda(models.Model):
    agenda = models.CharField(max_length=255)
    user = models.ForeignKey(User)

    def __unicode__(self):
        return "%s - %s" % (self.user, self.agenda)
