# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication
from tastypie import fields
from .models import Category, Article, Member
import pickle

class MemberResource(ModelResource):
	class Meta:
		queryset = Member.objects.all()
		# fields = ["email", "username"]
		resource_name = 'member'
	def dehydrate(self, bundle):
		cats = []
		for cat in bundle.obj.preferedCategoryIDs.all():
			cats.append(cat.name)
		bundle.data['preferedCategoryIDs'] = cats
		return bundle

 # class for handling authentication
class MyAuthentication(BasicAuthentication):
	def is_authenticated(self, request, **kwargs):
		return True
		# put here the logic to check username and password from request object
		# if the user is authenticated then return True otherwise return False


class UserResource(ModelResource):
	member = fields.OneToOneField(MemberResource, 'member', full=True)

	class Meta:
		authentication = MyAuthentication()
		queryset = User.objects.all()
		fields = ["email", "username"]
		resource_name = 'user'
		filtering  = {
			'username': ALL_WITH_RELATIONS
		}
	
	# def dehydrate(self, bundle):
	# 	bundle.data['twitter'] = bundle.obj.member.twitter
	# 	bundle.data['facebook'] = bundle.obj.member.facebook
	# 	bundle.data['gplus'] = bundle.obj.member.gplus
	# 	bundle.data['preferedCategoryIDs'] = bundle.obj.member.preferedCategoryIDs.values('name')
	# 	bundle.data['autoShare'] = bundle.obj.member.autoShare
	# 	bundle.data['geoloc'] = bundle.obj.member.geoloc
	# 	bundle.data['pays'] = bundle.obj.member.pays
	# 	bundle.data['ville'] = bundle.obj.member.ville
	# 	bundle.data['user'] = bundle.obj.member.user
		# return bundle


class ArticleResource(ModelResource):

	class Meta:
		queryset = Article.objects.order_by("category")
		resource_name = 'articles'
		fields = ['title', 'date', 'text', 'tags', 'category']
		authorization = Authorization()	
		

class CategoryResource(ModelResource):
	class Meta:
		queryset = Category.objects.all()
		resource_name = 'category'
		excludes = ['memberId']
		fields = ['name']
		authorization = Authorization()