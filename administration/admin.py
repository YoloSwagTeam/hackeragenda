from django.contrib import admin
from .models import UserSource


class UserSourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserSource, UserSourceAdmin)
