from django.conf.urls import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^phonebook/', include('phonebook.urls')),
    url(r'^qa/', include('qa.urls')),
    url(r'^orig/(.*)$', 'django.views.static.serve', {'document_root' : settings.MEDIA_ROOT}),
)
