from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="home.html"), name='home'),
    # url(r'^hackeragenda/', include('hackeragenda.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
