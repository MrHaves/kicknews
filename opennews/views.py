# -*- coding: utf-8 -*-

# Import django libs
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response,render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from django.template import RequestContext
from django.contrib.sessions.models import Session

# Import tools
from itertools import chain
from haystack.query import SearchQuerySet
from datetime import datetime
import mimetypes
from unicodedata import normalize
import feedparser
from dateutil import parser

# Import openNews datas
from forms import *
from models import *
from tools import *



# Define your views here

def home(request):
	"""The default view"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	# user = request.user

	return render(request, "index.html", locals())


def view_rss_feed(request, rssID):
	# Get the rss by its ID
	qs = RssFeed.objects.filter(id=rssID)
	# If doesn't exist, or if too bad, return empty entries for error
	if not qs or qs[0].mark < 5:
		return render(request, "viewrss.html", {'entries': None})
	# if exist and accepted, get entries
	else:
		rss = qs[0]
		entries = FeedEntry.objects.filter(rssfeed=rss)
		# if entries doesn't exist, add all the entries
		if not entries:
			feed = feedparser.parse(rss.url)
			entries = feed['entries']
			for x in entries:
				x['published'] = parser.parse(x['published']).replace(tzinfo=None)
				entry = FeedEntry(rssfeed=rss, title=x['title'], date=x['published'], link=x['link'], summary=x['summary'])
				entry.save()
		# if entries already exist, check updated date of rss feed and add only news entries
		else:
			feed = feedparser.parse(rss.url)
			entries = feed['entries']
			for x in entries:
				x['published'] = parser.parse(x['published']).replace(tzinfo=None)
				if x['published'] > rss.updatedDate:
					entry = FeedEntry(rssfeed=rss, title=x['title'], date=x['published'], link=x['link'], summary=x['summary'])
					entry.save()
			# Update the rss update date
			rss.updatedDate = parser.parse(feed['feed']['updated']).replace(tzinfo=None)
			rss.save()
		return render(request, "viewrss.html", {'rss':rss, 'entries':entries})


@login_required(login_url='/login/') # You need to be logged for this page
def add_rss_feed(request):
	"""View to add a rss feed"""
	# Check if POST datas had been sent
	if len(request.POST):
		# make a add rss form with the POST values
		form = add_rss_feed_form(request.POST)

		if form.is_valid():
			# If form is valid, get the url of the rss feed
			rss_feed = form.cleaned_data['rss_feed']
			# Try to find an existing rss feed
			qs = RssFeed.objects.filter(url=rss_feed)
			if not qs:
				# If doesn't exist, add it
				feed = feedparser.parse(rss_feed)
				rss = RssFeed(name=feed['feed']['title'], url=feed['href'], updatedDate=parser.parse(feed['feed']['updated']).replace(tzinfo=None), mark=0)
				rss.save()
				# Clean the form and send it again
				form = add_rss_feed_form()
				return render_to_response("add_rss.html", {'success': "Félicitation, votre flux rss est soumis. Veuillez attendre que les admins le modère.", 'form': form}, context_instance=RequestContext(request))
			else:
				return render_to_response("add_rss.html", {'error': "Ce flux a déjà été soumis. Veuillez attendre son acceptation", 'form': form}, context_instance=RequestContext(request))
		else:
			return render_to_response("add_rss.html", {'form': form}, context_instance=RequestContext(request))
	else:
		# Create an empty form and send it
		form = add_rss_feed_form()
		return render_to_response("add_rss.html", {'error': "Ce flux a déjà été soumis. Veuillez attendre son acceptation", 'form': form}, context_instance=RequestContext(request))



#### TODO ###
@login_required(login_url='/login/') # You need to be logged for this page
def rss_validator(request, id):
	if not request.user.is_staff:
		error = "Désolé, vous ne faites pas partie du staff, vous ne pouvez pas accéder à cette page. Un mail contenant votre identifiant a été envoyé aux modérateurs pour vérifier vos accès."
		return render_to_response("rss_validator.html", {'error': error}, context_instance=RequestContext(request))
	
	# Get all the rss
	qsFeed = RssFeed.objects.filter(mark__lt=5).order_by('name')
	qsVote = AdminVote.objects.filter(userId=request.user.id).values_list('feedId', flat=True)
	# Only take those whose logged user already vote
	rss_feeds = [rss for rss in qsFeed if rss.id not in qsVote]

	
	if id:
		qs = RssFeed.objects.filter(id=id)
		qsVote = AdminVote.objects.filter(userId=request.user.id).values_list('feedId', flat=True)
		if qs and (int(id) not in qsVote):
			rssfeed = qs[0]
			if request.GET.get('choice') == 'ok':
				rssfeed.mark += 1
				rssfeed.save()
				vote = AdminVote()
				vote.userId = request.user.id
				vote.feedId = id
				vote.save()
				return HttpResponseRedirect("/rss_validator")
			elif request.GET.get('choice') == 'trash':
				vote = AdminVote()
				vote.userId = request.user.id
				vote.feedId = id
				vote.save()
				return HttpResponseRedirect("/rss_validator")
			elif request.GET.get('choice') not in ['trash', 'ok']:
				error = "Désolé, ce choix n'existe pas. Veuillez vous contenter des boutons de vote."
				return render_to_response("rss_validator.html", {'rss_feeds': rss_feeds, 'error': error}, context_instance=RequestContext(request))
		else:
			error = "Désolé, vous ne pouvez pas voter pour ce flux. Veuillez utiliser le tableau."
			return render_to_response("rss_validator.html", {'rss_feeds': rss_feeds, 'error': error}, context_instance=RequestContext(request))

	return render_to_response("rss_validator.html", {'rss_feeds': rss_feeds}, context_instance=RequestContext(request))


def comment(request):
	article = Article.objects.get(id=request.POST.get('articleId'))
	member = Member.objects.get(id=request.POST.get('memberId'))
	comment = Comment(text=request.POST.get('commentText'), memberId=member,  articleId=article)
	comment.save()
	return render(request, "comment.html", locals())

def login_user(request):
	"""The view for login user"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat)

	# Already logged In ? => go Home
	if request.user.is_authenticated():
		return HttpResponseRedirect("/")

	# If you come from login required page, get the page url in "next"
	next = request.GET.get('next')

	# If form had been send
	if len(request.POST) > 0:
		# make a login form with the POST values
		form = login_form(request.POST)
		
		if form.is_valid():
			# If form is valid, try to authenticate the user with the POST datas
			s_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])

			if s_user is not None:
				# If the user exist, log him
				login(request, s_user)
				request.session['user_id'] = s_user.id
				if next is not None:
					# If you come from a login required page, redirect to it
					return HttpResponseRedirect(next)
				else:
					# Else go Home
					return HttpResponseRedirect("/")
			else:
				# If user does not exist, return to the login page & send the next params et the formular
				return render_to_response("login.html", {'categories': categories, 'form': form, 'next':next}, context_instance=RequestContext(request))
		else:
			# If form is not valid, return to the login page & send the next params et the formular
			return render_to_response("login.html", {'categories': categories, 'form': form, 'next':next}, context_instance=RequestContext(request))
	else:
		# If form is not send, it's the first visit.
		# Make an empty login form and send it to login template
		form = login_form()
		return render_to_response("login.html", {'categories': categories, 'form': form, 'next':next}, context_instance=RequestContext(request))


def logout_user(request):
	"""The view for logout user"""
	logout(request)
	next = request.GET.get('next')
	if next is not None:
		# If you come from a login required page, redirect to it
		return HttpResponseRedirect(next)
	else:
		# Else go Home
		return HttpResponseRedirect("/")


def register(request):
	"""The views for register new user"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat)

	# If form had been send
	if len(request.POST) > 0:
		# make a user registration form with the POST values
		form = user_create_form(request.POST)
		
		if form.is_valid():
			# If form is valid, create and try to authenticate the user with the POST datas
			user = form.save()
			# Get the password from the POST values
			pwd = form.cleaned_data['password1']
			# Try to authenticate the user
			s_user = authenticate(username=user.username, password=pwd)
			if s_user is not None:
				# If user exist, log him and go to his account management panel
				login(request, s_user)
				return HttpResponseRedirect('preferences')
			else:
				# if he does not exist, return to user registration page with form filled by the POST values
				return render_to_response("register.html", {'categories': categories, 'form': form}, context_instance=RequestContext(request))
		else:
			# if form is not valid, return to registration page
			return render_to_response("register.html", {'categories': categories, 'form': form}, context_instance=RequestContext(request))
	else:
		# if its you first visit, make an empty user registration form and send it
		form = user_create_form()
		return render_to_response("register.html", {'categories': categories, 'form': form}, context_instance=RequestContext(request))



@login_required(login_url='/login/') # You need to be logged for this page
def preferences(request):
	"""The view where logged user can modify their property"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat)

	# If form had been send
	if len(request.POST) > 0:
		# make a user preference form with the POST values
		form = user_preferences_form(request.POST)
		
		if form.is_valid():
			# If form is valid, save the user preferences and go Home
			form.save(request.user)
			return HttpResponseRedirect('/')
		else:
			# If not, send the preference form and the post datas
			return render_to_response("preferences.html", {'categories': categories, 'form': form}, context_instance=RequestContext(request))
	else:
		# if the form is not send try to find the member from the logged user
		try:
			member = request.user.member
		except Member.DoesNotExist:
			member = None
		
		if member is not None:
			# if member is not none, create preference form with user's datas
			form = user_preferences_form(instance=request.user.member)
			return render_to_response("preferences.html", {'categories': categories, 'form': form}, context_instance=RequestContext(request))
		else:
			# If member does not exist, send an empty form
			form = user_preferences_form()
			return render_to_response("preferences.html", {'categories': categories, 'form': form}, context_instance=RequestContext(request))	



def get_profile(request, userId):
	"""Show the public profile of a user. Get it by his id"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat)

	user = User.objects.filter(id=userId)[0]
	return render_to_response("public_profile.html", {'categories': categories, 'user': user})



def read_article(request, IDarticle):
	"""The view for reading an article"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat)
	# Get the article from the IDarticle params
	article = Article.objects.get(id=IDarticle)
	# Set the article category as active category
	catActive = article.category.url
	# Get the current user votes to know if he has already voted
	user_f_vote_qs = FiabilityVote.objects.filter(userId=request.user.id, articleId=IDarticle)
	if user_f_vote_qs: user_f_vote = user_f_vote_qs[0]
	else: user_f_vote = None

	user_q_vote_qs = QualityVote.objects.filter(userId=request.user.id, articleId=IDarticle)
	if user_q_vote_qs: user_q_vote = user_q_vote_qs[0]
	else: user_q_vote = None
	# Get the currents articles marks
	article_f_vote_qs = FiabilityVote.objects.filter(articleId=IDarticle).values_list('vote', flat=True)
	if article_f_vote_qs:
		article_f_note = round(float(sum(article_f_vote_qs))/float(len(article_f_vote_qs)),2)
	else:
		article_f_note = 0

	article_q_vote_qs = QualityVote.objects.filter(articleId=IDarticle).values_list('vote', flat=True)
	if article_q_vote_qs:
		article_q_note = round(float(sum(article_q_vote_qs))/float(len(article_q_vote_qs)),2)
	else:
		article_q_note = 0
	# Get the tags of the article
	tags = article.tags.all()
	if article.media:
		# If there is a media linked to the article, get the mime of it and the type of media
		mime = mimetypes.guess_type(article.media.url)[0]
		mediaType = mime[0:3]
	else:
		# If there is not, set False to mime et mediaType
		mime = False
		mediaType = False
	return render_to_response("article.html", {'article_f_note':article_f_note, 'article_q_note':article_q_note, 'user_f_vote':user_f_vote,'user_q_vote':user_q_vote, 'catActive':catActive, 'categories': categories,'article': article, 'mediaType': mediaType, 'mime': mime, 'tags': tags}, context_instance=RequestContext(request))	


@login_required(login_url='/login/') # You need to be logged for this page
def article_quality_vote_ajax(request):
	if len(request.POST) > 0:
		user_q_vote = QualityVote(articleId=request.POST.get('articleId'), userId=request.user.id, vote=request.POST.get('vote')).save()
	# Get the currents articles marks
	article_q_vote_qs = QualityVote.objects.filter(articleId=request.POST.get('articleId')).values_list('vote', flat=True)
	if article_q_vote_qs:
		article_q_note = round(float(sum(article_q_vote_qs))/float(len(article_q_vote_qs)),2)
	else:
		article_q_note = 0

	return render(request, "q_or_f_vote.html", locals())

@login_required(login_url='/login/') # You need to be logged for this page
def article_fiability_vote_ajax(request):
	if len(request.POST) > 0:
		user_f_vote = FiabilityVote(articleId=request.POST.get('articleId'), userId=request.user.id, vote=request.POST.get('vote')).save()
	# Get the currents articles marks
	article_f_vote_qs = FiabilityVote.objects.filter(articleId=request.POST.get('articleId')).values_list('vote', flat=True)
	if article_f_vote_qs:
		article_f_note = round(float(sum(article_f_vote_qs))/float(len(article_f_vote_qs)),2)
	else:
		article_f_note = 0

	return render(request, "q_or_f_vote.html", locals())


@login_required(login_url='/login/') # You need to be logged for this page
def write_article(request):
	"""The view for writing an article"""
	# Get the member from the request user
	member = Member.objects.get(user=request.user)

	# If form had been send
	if len(request.POST) > 0:
		# make a article form with the POST values
		form = article_form(request.POST, request.FILES)		
		if form.is_valid():
			# save the tags
			tags = request.POST['tagInput'].split(',')
			# If the form is correctly filled, check the geoloc status of the author
			if member.geoloc is not False:
				# Get coord from POST (an hidden input from template, filled by js)
				coordonnee = request.POST['coordonnee']
				# Save the article with the coord
				article = form.save(m_member=member, coord=coordonnee)
			else:
				# Save the article without the coord
				article = form.save(m_member=member)
			for tag in request.POST['tagInput'].split(','):
				if tag.isdigit():
					tagQuery = Tag.objects.get(id=tag)
					article.tags.add(tagQuery)
				else:
					qs = Tag(tag=tag)
					qs.save()
					article.tags.add(qs)
			article.save()
			return HttpResponseRedirect('/categories')
		else:
			# If it's not valid, send the form with POST datas
			return render_to_response("write.html", {'form': form, 'member':member}, context_instance=RequestContext(request))
	else:
		# If it's not valid, send an empty form
		form = article_form()
		return render_to_response("write.html", {'form': form, 'member':member}, context_instance=RequestContext(request))



def list_article(request, categorie):
	"""The view for listing the articles, depends on categorie"""
	# Get the category and put the name in a list
	categoriesQuerySet = Category.objects.all()
	categories = []
	for cat in categoriesQuerySet:
		categories.append(cat)
	
	if not Category.objects.filter(url=categorie) and categorie != "all":
		return render_to_response("liste.html", {'categories': categories, 'error': "Cette catégorie n'existe pas"})

	# Filter articles by category name
	if categorie == "all":
		articles = Article.objects.all()
		catActive = False
	else:
		articles = Article.objects.filter(category=Category.objects.filter(url=categorie)) # Here, .title() is to put the first letter in upperCase
		catActive = categorie

	
	# Get the size of each columns
	nbArticlePerCol = len(articles)/3
	# Init columns
	articlesCol1, articlesCol2, articlesCol3 = [], [], []
	
	# Fill each columns with articles
	counter = 1
	# Get logged member
	member = False
	if request.user.is_authenticated():
		qs = Member.objects.filter(user = request.user)
		if qs:
			member = qs[0]
		


	for article in articles:
		# Add the comments relatives to the current article
		article.comments = Comment.objects.filter(articleId=article.id)
		if counter <= nbArticlePerCol+1:
			articlesCol1.append(article)
		elif (counter > nbArticlePerCol+1) & (counter <= 2*nbArticlePerCol+2):
			articlesCol2.append(article)
		else:
			articlesCol3.append(article)
		counter += 1
		
	# Return the articles list, the categories list and the active categorie
	return render_to_response("liste.html", {'member': member, 'articles': articles, 'articlesCol1': articlesCol1, 'articlesCol2': articlesCol2, 'articlesCol3': articlesCol3, 'categories': categories, 'catActive': categorie}, context_instance=RequestContext(request))

# def search(request, words, categorie):
# 	"""The search view"""
# 	categoriesList = Category.objects.all()
# 	categories = []
# 	for cat in categoriesList:
# 		categories.append(cat.name)

	
# 	if len(request.POST) > 0:
# 		form = searchForm(request.POST)
# 		if form.is_valid():
# 			words = form.cleaned_data['searchWords'].split(' ')
# 		else:	
# 			return render_to_response("search.html", {'form': form, 'categories': categories, 'catActive': categorie.title()})
# 	else:
# 		form = searchForm()
# 		words = words.split('_')

# 	articles = []

# 	if categorie == "all":
# 		for word in words:
# 			articles = list(chain(articles, Article.objects.filter(Q(title__contains = word) | Q(text__contains = word))))
# 			tmp = Tag.objects.filter(tag = word )
# 			if len(tmp) is not 0:
# 				articles += tmp[0].article_set.all()

# 	else:
# 		for word in words:
# 			articles = list(chain(articles, Article.objects.filter(Q(category=Category.objects.filter(name=categorie.title())) & (Q(title__contains = word) | Q(text__contains = word)) )))
# 			tmp = Tag.objects.filter(tag = word)
# 			if len(tmp) is not 0:
# 				articles += tmp[0].article_set.all()
			

# 	return render_to_response("search.html", {'form': form, 'words': words, 'articles': list(set(articles)), 'categories': categories, 'catActive': categorie.title()})


