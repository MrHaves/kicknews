# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from .api import ArticleResource, MemberResource, CategoryResource, UserResource
from tastypie.api import Api
from .views import home, register, lireArticle, listerArticle, loginUser, logoutUser, preferences
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

v1_api = Api(api_name='v1')
v1_api.register(MemberResource())
v1_api.register(ArticleResource())
v1_api.register(CategoryResource())
v1_api.register(UserResource())

entry_resource = ArticleResource()

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
    url(r'^api/', include(v1_api.urls)),


    # url(r'^kicknews/', include('kicknews.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
