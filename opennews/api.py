# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication,ApiKeyAuthentication
from tastypie import fields
from .models import Category, Article, Member



class MemberResource(ModelResource):
	class Meta:
		authentication = ApiKeyAuthentication()
		queryset = Member.objects.all()
		resource_name = 'member'
		include_resource_uri = False
		allowed_methods = []
	
	def dehydrate(self, bundle):
		cats = []
		for cat in bundle.obj.preferedCategoryIDs.all():
			cats.append(cat.name)
		bundle.data['preferedCategoryIDs'] = cats
		return bundle


class UserResource(ModelResource):
	member = fields.OneToOneField(MemberResource, 'member', full=True)
	class Meta:
		authentication = ApiKeyAuthentication()
		queryset = User.objects.all()
		include_resource_uri = False
		fields = ["email", "username"]
		resource_name = 'user'
		filtering  = {
			'username': ALL_WITH_RELATIONS
		}




class CategoryResource(ModelResource):
	class Meta:
		queryset = Category.objects.all()
		resource_name = 'category'
		fields = ['name']
		include_resource_uri = False


class ArticleResource(ModelResource):
	class Meta:
		queryset = Article.objects.all()
		resource_name = 'articles'
		include_resource_uri = False
		authorization = Authorization()
	

	def dehydrate(self, bundle):
		bundle.data['category'] = bundle.obj.category.name.lower()
		return bundle	


		
