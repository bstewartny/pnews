from django.conf.urls import include, url
import portal.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'pnews.views.home', name='home'),
    # url(r'^pnews/', include('pnews.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin', include(admin.site.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^topics$',portal.views.topics),
    url(r'^sources$',portal.views.sources),
    url(r'^zeitgeist$',portal.views.zeitgeist),
    url(r'^memes$',portal.views.memes),
    url(r'^topics/$',portal.views.topics),
    url(r'^sources/$',portal.views.sources),
    url(r'^zeitgeist/$',portal.views.zeitgeist),
    url(r'^memes/$',portal.views.memes),
    url(r'^.*$',portal.views.index),
    url(r'^$',portal.views.index),
    url(r'^/$',portal.views.index)
]
