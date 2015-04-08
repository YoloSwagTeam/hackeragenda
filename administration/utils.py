from django.conf import settings
from django.contrib.auth.decorators import user_passes_test


def user_can_add_events(view):
    def test(user):
        return user.is_authenticated() and user.usersource_set.exists() and user.useragenda_set.filter(agenda=settings.AGENDA).exists()

    return user_passes_test(test)(view)
