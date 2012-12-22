# -*- coding: utf-8 -*-
from google.appengine.ext import db


# Create your models here.
class Member(db.Model):
	nickname = db.StringProperty()
	email = db.EmailProperty()
	password = db.StringProperty()
	twitter = db.StringProperty()
	facebook = db.StringProperty()
	gplus = db.StringProperty()
	preferedCategoryIDs = db.StringProperty()
	autoShare = bool
	geoloc = bool
	pays = db.StringProperty()
	ville = db.StringProperty()


class Category(db.Model):
	name = db.StringProperty()
	memberId = db.IntegerProperty()

class Article(db.Model):
	title = db.StringProperty()
	text = db.TextProperty()
	date = db.DateTimeProperty()
	published = bool
	validate = bool
	quality = db.IntegerProperty()
	tags = db.StringProperty()
	memberId = db.IntegerProperty(Member)
	category = db.IntegerProperty(Category)


class Comment(db.Model):
	text = db.StringProperty()
	articleId = db.IntegerProperty()
	memberId = db.IntegerProperty()

class Media(db.Model):
	title = db.StringProperty()
	url = db.LinkProperty()
	commentId = db.IntegerProperty()
	memberId = db.IntegerProperty()
	
