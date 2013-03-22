# ===================
# qa/urls.py
# ===================

from django.conf.urls import patterns, include, url

from .views import Compares 
from .views import BlankPages
from .views import CompareCollections
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import os

urlpatterns = patterns('',
    # Check if the page is blank
    url(r'^blank/?$', BlankPages.as_view()),

    # Compare two screenshots in order to estimate their 
    # similarity using SIFT features 
    url(r'^compare/?$', Compares.as_view()),

    # Compare a list of screenshots passed as URLs pairs
    url(r'^comparecollection/?$', CompareCollections.as_view()),

    # Display original image 
    #url(r'^photo/$', 'galery.views.photo'),
    url(r'^orig/(.*)$', 'django.views.static.serve', {'document_root' : os.path.join(os.path.dirname(__file__), 'orig')}),    
)

#..rest of url.py config...
urlpatterns += staticfiles_urlpatterns()
