from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

from .models import Source


def user_can_add_events(view):
    def test(user):
        return user.is_authenticated() and Source.objects.filter(users=user, agenda=settings.AGENDA).exists()

    return user_passes_test(test)(view)
