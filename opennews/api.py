# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication,ApiKeyAuthentication
from tastypie import fields
from .models import *



class MemberResource(ModelResource):
	class Meta:
		authentication = ApiKeyAuthentication()
		queryset = Member.objects.all()
		resource_name = 'member'
		include_resource_uri = False
		allowed_methods = []
	
	def dehydrate(self, bundle):
		"""Adding the user prefered catagories name"""
		cats = []
		for cat in bundle.obj.preferedCategoryIDs.all():
			cats.append(cat.name)
		bundle.data['preferedCategoryIDs'] = cats
		return bundle


class UserResource(ModelResource):
	member = fields.OneToOneField(MemberResource, 'member', full=True) #Member is linked to only one user according to the model
	class Meta:
		authentication = ApiKeyAuthentication()
		queryset = User.objects.all()
		include_resource_uri = False
		fields = ["email", "username"]
		resource_name = 'user'
		filtering  = {
			'username': ALL_WITH_RELATIONS
		}



class ArticleResource(ModelResource):
	class Meta:
		queryset = Article.objects.all()
		resource_name = 'articles'
		fields = ["date", "title", "text"]
		include_resource_uri = False
		authorization = Authorization()
		
	def dehydrate(self, bundle):
		"""adding articles tags and category"""
		bundle.data['memberId'] = "test"
		# bundle.data['category'] = bundle.obj.category.name
		# bundle.data['tags'] = []
		# for x in bundle.obj.tags.all():
		# 	bundle.data['tags'].append(x.tag)
		return bundle


class TagResource(ModelResource):
	class Meta:
		queryset = Tag.objects.all()
		resource_name = 'tags'
		fields = ['tag']
		include_resource_uri = False



class CategoryResource(ModelResource):
	class Meta:
		queryset = Category.objects.all()
		resource_name = 'category'
		fields = ['name']
		include_resource_uri = False
		filtering  = {
			'name': ALL_WITH_RELATIONS
		}

	def dehydrate(self, bundle):
		"""Adding categorie articles and tags of these articles"""
		bundle.data['articles'] = []
		for x in Article.objects.filter(category=bundle.obj, published=True).values('id','title', 'date', 'validate', 'quality', 'text', 'memberId'):
			x['member'] = User.objects.filter(id=x['memberId'])[0]
			x.pop("memberId")
			x['tags'] = []
			for t in Article.objects.filter(id=x['id'])[0].tags.all():
				x['tags'].append(t)
			bundle.data['articles'].append(x)
		return bundle

