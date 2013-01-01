# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url

from .views import home, register, lireArticle
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', home),
   	url(r'^register$', register),
   	url(r'^article/(\d{1})$', lireArticle),
    # url(r'^kicknews/', include('kicknews.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
