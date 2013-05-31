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

    url(r'^$', 'CiClops_web.views.index'),
    url(r'^ciclops/$', 'CiClops_web.views.index'),

    url(r'^pleiades/$', 'pleiades.views.index'),
    url(r'^pleiades/login/$', 'pleiades.views.login'),
    url(r'^pleiades/register/$', 'pleiades.views.register'),
    url(r'^pleiades/new_user/(?P<user>.+)/$', 'pleiades.views.new_user'),
    url(r'^pleiades/logout/$', 'pleiades.views.logout'),
    url(r'^pleiades/upload/$', 'pleiades.views.upload'),
    url(r'^pleiades/progress/$', 'pleiades.progress.progress'),
    url(r'^pleiades/progress/samples/(?P<view_as>.+)/(?P<jobName>.+)/$', 'pleiades.progress.samples'),
    url(r'^pleiades/progress/chart/(?P<view_as>.+)/(?P<jobName>.+)/$', 'pleiades.progress.chart'),
    url(r'^pleiades/results(?P<path>[\w._\s\-/()]*)/$', 'pleiades.views.results'),
    url(r'^pleiades/download(?P<path>[\w._\s\-/()]*)/$', 'pleiades.views.download_results'),

    url(r'^cidb/', include('cidb.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
