# -*- coding: utf-8 -*-
# Import django tools
from django.conf.urls import url
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.validators import email_re
from django.utils.dateformat import format
# Import tastypie tools
from tastypie.http import HttpUnauthorized, HttpForbidden
from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie.authentication import BasicAuthentication,ApiKeyAuthentication
from tastypie import fields
from tastypie.utils import trailing_slash
from tastypie.models import ApiKey
# Import opennews models
from opennews.models import *




class MemberResource(ModelResource):
	class Meta:
		authentication = ApiKeyAuthentication() # This resource requires to be logged in
		queryset = Member.objects.all() # Get all the member
		resource_name = 'member'
		include_resource_uri = False	# Remove the uri in the json
		allowed_methods = ['get']			# Only allows get actions (for now)
	
	def dehydrate(self, bundle):
		"""Adding the user prefered catagories name"""
		cats = []
		# Add the prefered categories name of the member
		for cat in bundle.obj.preferedCategoryIDs.all():
			cats.append(cat.name)
		bundle.data['preferedCategoryIDs'] = cats
		return bundle



class UserResource(ModelResource):
	member = fields.OneToOneField(MemberResource, 'member', full=True) #Member is linked to only one user according to the model
	class Meta:
		authentication = ApiKeyAuthentication()	# This resource requires to be logged in
		queryset = User.objects.all()	# Get all the user
		include_resource_uri = False	# Remove the uri in the json
		fields = ["email", "username"]	# Only keep the email and username fields
		resource_name = 'user'
		filtering  = {
			'username': ALL_WITH_RELATIONS	# The only result is your
		}

	# Redefine url for login and logout
	def prepend_urls(self):
		return [
			url(r"^(?P<resource_name>%s)/login%s$" %(self._meta.resource_name, trailing_slash()),self.wrap_view('login'), name="api_login"),
			url(r'^(?P<resource_name>%s)/logout%s$' %(self._meta.resource_name, trailing_slash()),self.wrap_view('logout'), name='api_logout'),
			url(r'^(?P<resource_name>%s)/register%s$' %(self._meta.resource_name, trailing_slash()),self.wrap_view('register'), name='api_register'),
		]

	# register method for mobile registration
	def register(self, request, **kwargs):
		# Allows POST request
		self.method_check(request, allowed=['post'])
		
		# Deserialize the JSon response
		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
		
		# Get the needed datas
		username = data.get('username', '')
		email = data.get('email', '')
		password1 = data.get('password1', '')
		password2 = data.get('password2', '')

		
		if email_re.match(email) == False : # If email data is not a good email, return error
			return self.create_response(request, {
				'success': False,
				'reason': 'email not valid',
			})
		elif password1 != password2:	# If password1 and password2 don't match, return error
			return self.create_response(request, {
				'success': False,
				'reason': "passwords don't match",
			})
		elif len(User.objects.filter(username=username)) != 0 : # the username is already taken, return error
			return self.create_response(request, {
				'success': False,
				'reason': 'user already exist',
			})
		elif len(User.objects.filter(email=email)) != 0 : # If email already exist, return error
			return self.create_response(request, {
				'success': False,
				'reason': 'email already in use',
			})
		else:	# If already is ok, let's go for regisrtation
			# create a user and authenticate him (needed for login)
			user = User.objects.create_user(username, email, password1)
			user = authenticate(username=username, password=password1)
			# If user exist and is active, log him
			if user:
				if user.is_active:
					login(request, user)
			
			# Create a member object and link the user to it
			member = Member()
			member.user = user
			member.save()

			# Create a dictionnary for json response and delete unuse datas
			member = member.__dict__
			del member["_state"]
			del member["user_id"]
			# Add his api_key
			api_key = ApiKey.objects.get(user=user).key
			member["api_key"] = api_key
			
			# Return success = True and the member object
			return self.create_response(request, {
				'success': True,
				'member' : member
			})	


	# login method witch check user authentification
	def login(self, request, **kwargs):
		# Allows POST request
		self.method_check(request, allowed=['post'])

		# Deserialize the JSon response
		data = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))

		# Get the needed datas
		username = data.get('username', '')
		password = data.get('password', '')

		# Try to authenticate the user
		user = authenticate(username=username, password=password)
		# If user exist and is active
		if user:
			if user.is_active:
				# Get the associated member
				member = Member.objects.get(user_id=user.id).__dict__
				del member["_state"]
				del member["user_id"]
				# Add the ApiKey
				api_key = ApiKey.objects.get(user=user).key
				member["api_key"] = api_key
				# Log the user
				login(request, user)
				# Return success=True and the member object
				return self.create_response(request, {
					'success': True,
					'member': member,
				})
			else:
				# If user not active, return success = False and disabled
				return self.create_response(request, {
					'success': False,
					'reason': 'disabled',
				}, HttpForbidden )
		else:
			# If user does not exist, return success=False and incorrect
			return self.create_response(request, {
				'success': False,
				'reason': 'incorrect',
			}, HttpUnauthorized )

	# logout user
	def logout(self, request, **kwargs):
		# Allows GET request
		self.method_check(request, allowed=['get'])
		# If user exist and is log, Logout
		if request.user and request.user.is_authenticated():
			logout(request)
			return self.create_response(request, { 'success': True })
		else:
			# Else, return Unauthorized
			return self.create_response(request, { 'success': False }, HttpUnauthorized)





class ArticleResource(ModelResource):
	author = fields.ForeignKey(MemberResource, 'memberId', full=True) #Member is linked to only one user according to the model
	class Meta:
		queryset = Article.objects.all() # Get all the articles
		resource_name = 'articles'
		fields = ["date", "title", "text"] # Keep only date, title and text
		excludes = ['published', 'validated', 'coord', 'category', 'quality']
		include_resource_uri = False		# Remove uri datas
		authorization = Authorization()
		
	def dehydrate(self, bundle):
		"""adding articles tags and category"""
		# Get the author of the article
		bundle.data['author'] = bundle.data["author"].obj
		# get the timestamp of the date
		bundle.data['date'] = format(bundle.data['date'], 'U')

		# bundle.data['category'] = bundle.obj.category.name
		# bundle.data['tags'] = []
		# for x in bundle.obj.tags.all():
		# 	bundle.data['tags'].append(x.tag)
		return bundle


class TagResource(ModelResource):
	class Meta:
		queryset = Tag.objects.all() 	# Get all the tags
		resource_name = 'tags'
		fields = ['tag'] 				# Just keep the tag field
		include_resource_uri = False 	# Remove the uri data



class CategoryResource(ModelResource):
	class Meta:
		queryset = Category.objects.all() 	# Get all the categories
		resource_name = 'categories'
		fields = ['name'] 					# just keep the name
		include_resource_uri = False 		# Remove the uri
		filtering  = {
			'name': ALL_WITH_RELATIONS		# Filte on the name. E.g : http://bottlenews.cc/api/v1/categories/?format=json&name=sciences
		}

	def dehydrate(self, bundle):
		"""Adding categorie articles and tags of these articles"""
		bundle.data['articles'] = []
		# Here we get all the value for each object we need
		for x in Article.objects.filter(category=bundle.obj, published=True).values('id','title', 'date', 'validate', 'quality', 'text', 'memberId'):
			# Get the member
			x['author'] = Member.objects.get(id=x['memberId'])
			# Remove the memberId field
			x.pop("memberId")
			# Get the timestamp
			x['date'] = format(x['date'], 'U')
			# Add the tags
			x['tags'] = []
			for t in Article.objects.filter(id=x['id'])[0].tags.all():
				x['tags'].append(t)
			bundle.data['articles'].append(x)
		return bundle

