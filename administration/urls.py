from django.conf.urls import patterns, url


urlpatterns = patterns('administration.views',
    url(r'^$', 'dashboard', name='administration_dashboard'),
)
