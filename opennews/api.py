# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from tastypie import fields
from .models import Category, Article, Member

class MemberResource(ModelResource):
	class Meta:
		queryset = Member.objects.all()
		resource_name = 'member'

class ArticleResource(ModelResource):

	class Meta:
		queryset = Article.objects.order_by("category")
		resource_name = 'articles'
		excludes = ['published', 'validate', 'quality', 'memberId']
		fields = ['title', 'date', 'text', 'tags', 'category']
		authorization = Authorization()
		

class CategoryResource(ModelResource):
	user = fields.ForeignKey(MemberResource, 'member')

	class Meta:
		queryset = Category.objects.all()
		resource_name = 'category'
		excludes = ['memberId']
		fields = ['name']
		authorization = Authorization()