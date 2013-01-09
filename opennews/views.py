# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response,render
from django.contrib.auth.models import User
from forms import UserCreateForm
from opennews.models import *
import datetime

def home(request):
	foo = datetime.datetime.now()
	return render(request, "index.html", locals())

def register(request):
	if len(request.POST) > 0:
		form = UserCreateForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/')
		else:
			return render_to_response("register.html", {'form': form})
	else:
		form = UserCreateForm()
		return render_to_response("register.html", {'form': form})

def lireArticle(request, IDarticle):
	articles = Article.objects.filter(id=IDarticle)
	return render_to_response("article.html", {'articles': articles})

def listerArticle(request, categorie):
	if categorie == "all":
		articles = Article.objects.all()
	else:
		articles = Article.objects.filter(category=Category.objects.filter(name=categorie.lower()))

	return render_to_response("liste.html", {'articles': articles})