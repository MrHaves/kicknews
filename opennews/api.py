# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.validators import email_re
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication,ApiKeyAuthentication
from tastypie import fields
from .models import *
from tastypie.utils import trailing_slash
from tastypie.models import ApiKey



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
		tst = 1
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

	# Redefine url for login and logout
	def override_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/login%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('login'), name="api_login"),
			url(r'^(?P<resource_name>%s)/logout%s$' %(self._meta.resource_name, trailing_slash()),self.wrap_view('logout'), name='api_logout'),
			url(r'^(?P<resource_name>%s)/register%s$' %(self._meta.resource_name, trailing_slash()),self.wrap_view('register'), name='api_register'),
		]

	# register method for mobile registration
	def register(self, request, **kwargs):
		self.method_check(request, allowed=['post'])
		
		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
		
		username = data.get('username', '')
		email = data.get('email', '')
		password1 = data.get('password1', '')
		password2 = data.get('password2', '')

		if !email_re.match(email):
			return self.create_response(request, {
				'success': False,
				'reason': 'email not valid',
			})
		elif password1 != password2:
			return self.create_response(request, {
				'success': False,
				'reason': "passwords don't match",
			})
		elif User.objects.get(username=username) is not None:
			return self.create_response(request, {
				'success': False,
				'reason': 'user already exist',
			})
		elif User.objects.get(email=email) is not None:
			return self.create_response(request, {
				'success': False,
				'reason': 'email already in use',
			})
		else:
			user = User.objects.create_user(username, email, password1)
			return self.create_response(request, {
				'success': True,
			})


	# login method witch check user authentification
	def login(self, request, **kwargs):
		self.method_check(request, allowed=['post'])

		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

		username = data.get('username', '')
		password = data.get('password', '')

		user = authenticate(username=username, password=password)
		member = Member.objects.get(user_id=user.id).__dict__
		del member["_state"]
		del member["user_id"]
		api_key = ApiKey.objects.get(user=user).key
		member["api_key"] = api_key
		if user:
			if user.is_active:
				login(request, user)
				return self.create_response(request, {
					'success': True,
					'member': member,
				})
			else:
				return self.create_response(request, {
					'success': False,
					'reason': 'disabled',
				}, HttpForbidden )
		else:
			return self.create_response(request, {
				'success': False,
				'reason': 'incorrect',
			}, HttpUnauthorized )

	# logout user
	def logout(self, request, **kwargs):
		self.method_check(request, allowed=['get'])
		if request.user and request.user.is_authenticated():
			logout(request)
			return self.create_response(request, { 'success': True })
		else:
			return self.create_response(request, { 'success': False }, HttpUnauthorized)





class ArticleResource(ModelResource):
	class Meta:
		queryset = Article.objects.all()
		resource_name = 'articles'
		fields = ["date", "title", "text"]
		include_resource_uri = False
		authorization = Authorization()
		excludes = ['published', 'validated', 'coord', 'category', 'quality']
		
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

