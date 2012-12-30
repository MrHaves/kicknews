# -*- coding: utf-8 -*-
from django.db import models
# Create your models here.

class Member(models.Model):
	nickname = models.CharField(max_length=255);
	email = models.EmailField(max_length=50);
	password = models.CharField(max_length=30);
	twitter = models.CharField(max_length=100);
	facebook = models.CharField(max_length=255);
	gplus = models.CharField(max_length=255);
	preferedCategoryIDs = models.CharField(max_length=255);
	autoShare = models.BooleanField();
	geoloc = models.BooleanField();
	pays = models.CharField(max_length=3);
	ville = models.CharField(max_length=255);

	def __unicode__(self):
		return self.nickname

class Category(models.Model):
	name = models.CharField(max_length=255);
	memberId = models.ForeignKey(Member);

	def __unicode__(self):
		return self.name

class Article(models.Model):
	title = models.CharField(max_length=255);
	text = models.TextField();
	date = models.DateTimeField(auto_now_add=True);
	published = models.BooleanField();
	validate = models.BooleanField();
	quality = models.IntegerField();
	tags = models.CharField(max_length=255);
	memberId = models.ForeignKey(Member);
	category = models.ForeignKey(Category);

	def __unicode__(self):
		return self.title

class Comment(models.Model):
	text = models.CharField(max_length=255);
	articleId = models.ForeignKey(Article);
	memberId = models.ForeignKey(Member);

	def __unicode__(self):
		if len(self.text) > 20:
			return self.text[:19] + "..."
		else:
			return selft.text

class Media(models.Model):
	title = models.CharField(max_length=255);
	url = models.URLField();
	commentId = models.ForeignKey(Comment);
	memberId = models.ForeignKey(Member);

	def __unicode__(self):
		return self.title