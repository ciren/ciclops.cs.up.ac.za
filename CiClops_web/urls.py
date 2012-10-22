from django.conf.urls import patterns, include, url
from django.views.static import * 
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CiClops_web.views.home', name='home'),
    # url(r'^CiClops_web/', include('CiClops_web.foo.urls')),

    url(r'^ciclops/$', 'CiClops_web.views.index'),

    url(r'^pleiades/$', 'pleiades.views.index'),
    url(r'^pleiades/login/$', 'pleiades.views.login'),
    url(r'^pleiades/upload/$', 'pleiades.views.upload'),
    url(r'^pleiades/(?P<name>\w+)/$', 'pleiades.views.user'),
    url(r'^pleiades/(?P<name>\w+)/results(?P<path>[\w._\s\-/]*)/$', 'pleiades.views.results'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
