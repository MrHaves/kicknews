# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,render
# from django.core.exceptions import DoesNotExist
from django.contrib.auth.models import User
from forms import UserCreateForm, UserPreferencesForm, loginForm, ArticleForm
from django.contrib.auth import authenticate, login, logout
from opennews.models import *
import datetime
import mimetypes
from tastypie.models import ApiKey

def home(request):
	"""The default view"""
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
		form = UserCreateForm(request.POST)
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
	mime = "image/pg" #mimetypes.guess_type(article.media.url)[0]
	mediaType = ""
	return render_to_response("article.html", {'articles': articles, 'mediaType': mediaType, 'mime': mime})

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

