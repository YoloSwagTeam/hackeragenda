from django.urls import path, include

from . import views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("password_change/", views.password_change, name="password_change"),
    path(
        "password_change/done/", views.password_change_done, name="password_change_done"
    ),
    path("", include("django.contrib.auth.urls")),
]
