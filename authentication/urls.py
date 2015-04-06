from django.conf.urls import patterns, url, include


urlpatterns = patterns('authentitifaction.views',
    url(r'^', include("django.contrib.auth.urls"), name=''),
)
