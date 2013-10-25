from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^$', 'frace.views.index'),
    url(r'new/$', 'frace.views.new_job'),
    url(r'upload/$', 'frace.views.upload')
)
