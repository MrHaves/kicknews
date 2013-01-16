# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields
from .models import Category, Article

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'

class ArticleResource(ModelResource):
	user = fields.ForeignKey(UserResource, 'user')

	class Meta:
		queryset = Article.objects.order_by("category")
		resource_name = 'articles'
		authorization = Authorization()
		

class CategoryResource(ModelResource):
	user = fields.ForeignKey(UserResource, 'user')

	class Meta:
		queryset = Category.objects.all()
		resource_name = 'category'
		authorization = Authorization()