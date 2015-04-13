from django.contrib.auth import views as auth


def login(request):
    return auth.login(request, template_name="registration/login.haml")


def password_change(request):
    return auth.password_change(request, template_name="registration/password_change_form.haml")
