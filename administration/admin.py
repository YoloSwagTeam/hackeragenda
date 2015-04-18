from django.contrib import admin
from .models import Source


class SourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(Source, SourceAdmin)
