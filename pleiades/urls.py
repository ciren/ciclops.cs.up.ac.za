from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^login/$', 'pleiades.views.login'),
    url(r'^register/$', 'pleiades.views.register'),
    url(r'^new_user/(?P<user>.+)/$', 'pleiades.views.new_user'),
    url(r'^logout/$', 'pleiades.views.logout'),
    url(r'^upload/$', 'pleiades.views.upload'),
    url(r'^progress/$', 'pleiades.progress.progress'),
    url(r'^progress/samples/(?P<view_as>.+)/(?P<jobName>.+)/$', 'pleiades.progress.samples'),
    url(r'^progress/chart/(?P<view_as>.+)/(?P<jobName>.+)/$', 'pleiades.progress.chart'),
    url(r'^results(?P<path>[\w._\s\-/()]*)/$', 'pleiades.views.results'),
    url(r'^download(?P<path>[\w._\s\-/()]*)/$', 'pleiades.views.download_results'),
    url(r'', 'pleiades.views.index'),
)
