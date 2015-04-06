from django.contrib.auth import views as auth


def login(request):
    return auth.login(request, template_name="registration/login.haml")
