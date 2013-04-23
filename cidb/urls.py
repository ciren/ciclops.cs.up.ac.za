from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^search/$', 'cidb.views.search'),
    url(r'^download/(.*)/$', 'cidb.views.download'),
)
