# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):
    dependencies = [
        ("taggit", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("source", models.CharField(max_length=255)),
                ("color", models.CharField(max_length=255, null=True, blank=True)),
                ("text_color", models.CharField(max_length=255, null=True, blank=True)),
                (
                    "border_color",
                    models.CharField(max_length=255, null=True, blank=True),
                ),
                ("url", models.URLField()),
                ("all_day", models.BooleanField(default=False)),
                ("start", models.DateTimeField()),
                ("end", models.DateTimeField(null=True, blank=True)),
                ("location", models.CharField(max_length=255, null=True, blank=True)),
                ("agenda", models.CharField(max_length=255)),
                ("lon", models.FloatField(default=None, null=True, blank=True)),
                ("lat", models.FloatField(default=None, null=True, blank=True)),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        to="taggit.Tag",
                        through="taggit.TaggedItem",
                        help_text="A comma-separated list of tags.",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
