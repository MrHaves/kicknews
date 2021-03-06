# -*- coding: utf-8 -*-
# import django libs
from django.conf.urls import patterns, include, url
# import tastypie tools
from tastypie.api import Api
# import opennews datas
from api import *
from views import *
import datetime

from haystack.views import SearchView  
from haystack.query import SearchQuerySet 

# add api resources
v1_api = Api(api_name='v1')
v1_api.register(MemberResource())
v1_api.register(ArticleResource())
v1_api.register(CategoryResource())
v1_api.register(UserResource())
v1_api.register(TagResource())
v1_api.register(CommentResource())

sqs = SearchQuerySet().filter(date__gte=(datetime.datetime.now() - datetime.timedelta(days=7*100))).order_by('quality', '-date')

urlpatterns = patterns('',
    # opennews urls
    url(r'^$', list_article, {'categorie':"all"}),
    url(r'^home$', home),
    url(r'^addfeed$', add_rss_feed),
    url(r'^rss_validator$', rss_validator, {'id':False}),
    url(r'^rss_validator/(\d+)$', rss_validator),
    url(r'^viewsrss/(\d+)$', view_rss_feed),
    url(r'^comment$', comment),
    url(r'^quality_vote$', article_quality_vote_ajax),
    url(r'^fiability_vote$', article_fiability_vote_ajax),
   	url(r'^register$', register),
    url(r'^login/$', login_user),
    url(r'^logout/$', logout_user),
    url(r'^preferences$', preferences),
    url(r'^write$', write_article),
    url(r'^profile/(\d+)$', get_profile),
   	url(r'^articles/(\d+)$', read_article),
   	url(r'^categories/(\w+)$', list_article),
   	url(r'^categories/$', list_article, {'categorie':"all"}),
    url(r'^search/',  
                           SearchView(  
                               load_all=False,  
                               searchqueryset=sqs,  
                               ),  
                           name='haystack_search',  
                           ),  
    url(r'^api/', include(v1_api.urls)),
)
