# -*- coding: utf-8 -*-
# import django libs
from django.conf.urls import patterns, include, url
# import tastypie tools
from tastypie.api import Api
# import opennews datas
from api import *
from views import *

# add api resources
v1_api = Api(api_name='v1')
v1_api.register(MemberResource())
v1_api.register(ArticleResource())
v1_api.register(CategoryResource())
v1_api.register(UserResource())
v1_api.register(TagResource())



urlpatterns = patterns('',
    # opennews urls
    url(r'^$', home),
   	url(r'^register$', register),
    url(r'^login/$', login_user),
    url(r'^logout/$', logout_user),
    url(r'^preferences$', preferences),
    url(r'^write$', write_article),
    url(r'^profile/(\d+)$', get_profile),
   	url(r'^articles/(\d+)$', read_article),
   	url(r'^categories/(\w+)$', list_article),
   	url(r'^categories/$', list_article, {'categorie':"all"}),
    # url(r'^search/(\w+)/(\w+)$', search),
    # url(r'^search/(\w+)$', search, {'categorie':"all"}),
    # url(r'^search/$', search, {'words':"", 'categorie':"all"}),
    url(r'^search/', include('haystack.urls')),
    url(r'^api/', include(v1_api.urls)),
)
