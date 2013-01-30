# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,render
# from django.core.exceptions import DoesNotExist
from django.contrib.auth.models import User
from forms import UserCreateForm, UserPreferencesForm, loginForm, ArticleForm, searchForm
from django.contrib.auth import authenticate, login, logout
from opennews.models import *
from itertools import chain
from django.db.models import Q
import datetime
import mimetypes
from tastypie.models import ApiKey

def home(request):
	"""The default view"""
	#articles = Article.objects.filter(tag in tags)
	foo = datetime.datetime.now()
	user = request.user
	return render(request, "index.html", locals())


def loginUser(request):
	"""The view for login user"""
	if request.user.is_authenticated():
		return HttpResponseRedirect("/")

	next = request.GET.get('next')
	if len(request.POST) > 0:
		form = loginForm(request.POST)
		if form.is_valid():
			s_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
			if s_user is not None:
				login(request, s_user)
				if next is not None:
					return HttpResponseRedirect(next)
				else:
					return HttpResponseRedirect("/")
			else:
				return render_to_response("login.html", {'form': form, 'next':next})
		else:
			return render_to_response("login.html", {'form': form, 'next':next})
	else:
		form = loginForm()
		return render_to_response("login.html", {'form': form, 'next':next})


def logoutUser(request):
	"""The view for logout user"""
	logout(request)
	return HttpResponseRedirect('/')


def register(request):
	"""The views for register new user"""
	if len(request.POST) > 0:
		# Create a form for User registration
		form = UserCreateForm(request.POST)
		# Check if form is valid
		if form.is_valid():
			user = form.save()
			pwd = form.cleaned_data['password1']
			s_user = authenticate(username=user.username, password=pwd)
			if s_user is not None:
				login(request, s_user)
				return HttpResponseRedirect('preferences')
			else:
				return render_to_response("register.html", {'form': form})
		else:
			return render_to_response("register.html", {'form': form})
	else:
		form = UserCreateForm()
		return render_to_response("register.html", {'form': form})



@login_required(login_url='/login/')
def preferences(request):
	api_key = ApiKey.objects.filter(user=request.user)
	"""The view where logged user can modify their property"""
	if len(request.POST) > 0:
		form = UserPreferencesForm(request.POST)
		if form.is_valid():
			form.save(request.user)
			return HttpResponseRedirect('/')
		else:
			return render_to_response("preferences.html", {'form': form, 'api_key': api_key[0].key})
	else:
		try:
			member = request.user.member
		except Member.DoesNotExist:
			member = None
		
		if member is not None:
			form = UserPreferencesForm(instance=request.user.member)
			return render_to_response("preferences.html", {'form': form, 'api_key': api_key[0].key})
		else:
			form = UserPreferencesForm()
			return render_to_response("preferences.html", {'form': form})	


def get_profile(request, userId):
	"""Show the public profile of a user. Get it by his id"""
	user = User.objects.filter(id=userId)[0]
	return render_to_response("public_profile.html", {'user': user})


def lireArticle(request, IDarticle):
	"""The view for reading an article"""
	articles = Article.objects.filter(id=IDarticle)
	article = articles[0]
	tags = article.tags.all()
	if article.media:
		mime = mimetypes.guess_type(article.media.url)[0]
		mediaType = mime[0:3]
	else:
		mime = False
		mediaType = False
	return render_to_response("article.html", {'articles': articles, 'mediaType': mediaType, 'mime': mime, 'tags': tags})

@login_required(login_url='/login/')
def write_article(request):
	"""The view for writing an article"""
	member = Member.objects.filter(user=request.user)[0]
	if len(request.POST) > 0:
		form = ArticleForm(request.POST, request.FILES)
		if form.is_valid():
			if member.geoloc is not False:
				coordonnee = request.POST['coordonnee']
				article = form.save(m_member=member, coord=coordonnee)
			else:
				article = form.save(m_member=member)
			return HttpResponseRedirect('/categories')
		else:
			return render_to_response("write.html", {'form': form, 'member':member})
	else:
		form = ArticleForm()
		return render_to_response("write.html", {'form': form, 'member':member})


def listerArticle(request, categorie):
	"""The view for listing the articles, depends on categorie"""
	categoriesList = Category.objects.all()
	categories = []
	for cat in categoriesList:
		categories.append(cat.name)
	if categorie == "all":
		articles = Article.objects.all()
	else:
		articles = Article.objects.filter(category=Category.objects.filter(name=categorie.title()))

	return render_to_response("liste.html", {'articles': articles, 'categories': categories, 'catActive': categorie.title()})

def search(request, words, categorie):
	"""The search view"""
	categoriesList = Category.objects.all()
	categories = []
	for cat in categoriesList:
		categories.append(cat.name)

	
	if len(request.POST) > 0:
		form = searchForm(request.POST)
		if form.is_valid():
			words = form.cleaned_data['searchWords'].split(' ')
		else:	
			return render_to_response("search.html", {'form': form, 'categories': categories, 'catActive': categorie.title()})
	else:
		form = searchForm()
		words = words.split('_')

	articles = []

	if categorie == "all":
		for word in words:
			articles = list(chain(articles, Article.objects.filter(Q(title__contains = word) | Q(text__contains = word))))
			tmp = Tag.objects.filter(tag = word )
			if len(tmp) is not 0:
				articles += tmp[0].article_set.all()

	else:
		for word in words:
			articles = list(chain(articles, Article.objects.filter(Q(category=Category.objects.filter(name=categorie.title())) & (Q(title__contains = word) | Q(text__contains = word)) )))
			tmp = Tag.objects.filter(tag = word)
			if len(tmp) is not 0:
				articles += tmp[0].article_set.all()
			

	return render_to_response("search.html", {'form': form, 'words': words, 'articles': list(set(articles)), 'categories': categories, 'catActive': categorie.title()})

