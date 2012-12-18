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
	memberId = db.ForeignKey(Member)

class Article(db.Model):
	title = db.StringProperty()
	text = db.Text
	date = db.DateTimeField(auto_now_add=True)
	published = bbool
	validate = bool
	quality = db.IntegerField()
	tags = db.StringProperty()
	memberId = db.ForeignKey(Member)
	category = db.ForeignKey(Category)


class Comment(db.Model):
	text = db.CharField(max_length=255)
	articleId = db.ForeignKey(Article)
	memberId = db.ForeignKey(Member)

class Media(db.Model):
	title = db.CharField(max_length=255)
	url = db.URLField()
	commentId = db.ForeignKey(Comment)
	memberId = db.ForeignKey(Member)
	
