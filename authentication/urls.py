from django.conf.urls import patterns, url, include


urlpatterns = patterns('authentication.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^password_change/$', 'password_change', name='password_change'),
    url(r'^', include("django.contrib.auth.urls")),
)
