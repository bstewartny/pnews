from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pnews.views.home', name='home'),
    # url(r'^pnews/', include('pnews.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^topics$','portal.views.topics',name='topics'),
    url(r'^sources$','portal.views.sources',name='sources'),
    url(r'^.*$','portal.views.index',name='index')
)
