from django.conf.urls.defaults import *

print "Hello"

urlpatterns = patterns('',
    url(r'^$', 'frace.views.index'),
    url(r'new/$', 'frace.views.new_job')
)
