# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from opennews.api import EntryResource

from .views import home, register, lireArticle, listerArticle, preferences, loginUser, logoutUser
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

entry_resource = EntryResource()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', home),
   	url(r'^register$', register),
    #?next=/preferences
    url(r'^login/$', loginUser),
    url(r'^logout/$', logoutUser),
    url(r'^preferences$', preferences),
   	url(r'^articles/(\d{1})$', lireArticle),
   	url(r'^categories/(\w+)$', listerArticle),
   	url(r'^categories/$', listerArticle, {'categorie':"all"}),
    (r'^api/', include(entry_resource.urls)),
    # urls.py

    # url(r'^kicknews/', include('kicknews.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
