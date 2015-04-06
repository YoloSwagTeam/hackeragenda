from django.db import models
from django.contrib.auth.models import User


class UserSource(models.Model):
    source = models.CharField(max_length=255)
    user = models.OneToOneField(User)
