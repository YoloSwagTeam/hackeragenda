from django.contrib import admin
from .models import UserSource, UserAgenda


class UserSourceAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserSource, UserSourceAdmin)


class UserAgendaAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserAgenda, UserAgendaAdmin)
