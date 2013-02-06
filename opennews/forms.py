# -*- coding: utf-8 -*-
# Import django tools
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput
# Import opennews models
from opennews.models import Member, Article


class login_form(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class user_create_form(UserCreationForm):
    # Make the email field required
    email = forms.EmailField(required=True)

    class Meta:
        # Use the user model to create the formular but only with username, email and passowrds fields
        model = User
        fields = ("username", "email", "password1", "password2")

    # Override the save method
    def save(self, commit=True):
        # Create user from the forms datas and set the email field manually, but DON'T commit
        user = super(user_create_form, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        
        # When we want to commit (everytimes), 
        # save the user, create, link and saveth member.
        if commit:
            user.save()
            member = Member()
            member.user = user
            member.save()
        return user



class article_form(ModelForm):
    class Meta:
        # Use the article model to create the formular but without memberId, quality, validate and tags fields
        model = Article
        exclude = ('memberId','quality', 'validate', 'tags')

    # Override the save method   
    def save(self, m_member, coord=None, commit=True):
        # Create article from the forms datas and set the memberId field manually, but DON'T commit
        article = super(article_form, self).save(commit=False)
        article.memberId = m_member
        # Add coordinates if author agree
        if coord is not None:
            article.coord = coord
        article.save()
        return article


class user_preferences_form(ModelForm):
    class Meta:
        # Use the member model to create the formular but without user field
        model = Member
        exclude = ('user',)

    # Override the save method   
    def save(self, m_user, commit=True):
        if m_user.member is not None:
            # If m_user is defined, use his member and override the values
            member = m_user.member
            member.twitter = self.cleaned_data['twitter']
            member.facebook = self.cleaned_data['facebook']
            member.gplus = self.cleaned_data['gplus']
            member.geoloc = self.cleaned_data['geoloc']
            member.pays = self.cleaned_data['pays']
            member.ville = self.cleaned_data['ville']
            member.autoShare = self.cleaned_data['autoShare']
            member.preferedCategoryIDs = self.cleaned_data['preferedCategoryIDs']
            member.maxArticle = self.cleaned_data['maxArticle']
        else:    
            # Else, create and empty member and save it without commit         
            member = super(user_preferences_form, self).save(commit=False)
        
        # When we want to commit (everytimes), 
        # link the user and save the member
        if commit:
            member.user = m_user
            member.save()
        return member

# Create a search formular
class search_form(forms.Form):
    searchWords = forms.CharField(required=True)
