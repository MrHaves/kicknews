from google.appengine.ext import db
# Create your models here.

class Article(models.Model):
	title = models.CharField(max_length=255);
	text = models.TextField();
	date = models.DateTimeField(auto_now_add=true);
	published = models.BooleanField();
	validate = models.BooleanField();
	quality = models.IntegerField();
	tags = models.CharField(max_length=255);
	memberId = models.ForeignKey(Member);
	category = models.ForeignKey(Category);

class Member(models.Model):
	nickname = models.CharField(max_length=255);
	email = models.EmailField(max_length=50);
	password = models.CharField(max_length=30);
	twitter = models.(max_length=100);
	facebook = models.CharField(max_length=255);
	gplus = models.CharField(max_length=255);
	preferedCategoryIDs = models.CharField(max_length=255);
	autoShare = models.BooleanField();
	geoloc = models.BooleanField();
	pays = models.CharField(max_length=2);
	ville = models.CharField(max_length=255);

class Comment(models.Model):
	text = models.CharField();
	articleId = models.ForeignKey(Article);
	memberId = models.ForeignKey(Member);

class Media(models.Model):
	title = models.CharField(max_length=255);
	url = models.URLField();
	commentId = models.ForeignKey(Comment);
	memberId = models.ForeignKey(Member);
	
class Category(models.Model):
	name = models.CharField(max_length=255);
	memberId = models.ForeignKey(Member);


