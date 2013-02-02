# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from opennews.models import Member, Article
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.forms.widgets import PasswordInput


class login_form(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class user_create_form(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(user_create_form, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            member = Member()
            member.user = user
            member.save()
        return user

class article_form(ModelForm):
    class Meta:
        model = Article
        exclude = ('memberId','quality', 'validate', 'tags')

    def save(self, m_member, coord=None, commit=True):
        article = super(article_form, self).save(commit=False)
        article.memberId = m_member
        if coord is not None:
            article.coord = coord
        article.save()

class user_preferences_form(ModelForm):
    class Meta:
        model = Member
        exclude = ('user',)

    def save(self, m_user, commit=True):
        if m_user.member is not None:
            member = m_user.member
            member.twitter = self.cleaned_data['twitter']
            member.facebook = self.cleaned_data['facebook']
            member.gplus = self.cleaned_data['gplus']
            member.geoloc = self.cleaned_data['geoloc']
            member.pays = self.cleaned_data['pays']
            member.ville = self.cleaned_data['ville']
            member.autoShare = self.cleaned_data['autoShare']
            member.preferedCategoryIDs = self.cleaned_data['preferedCategoryIDs']
        else:            
            member = super(UserPreferencesForm, self).save(commit=False)
        if commit:
            member.user = m_user
            member.save()
        return member

class search_form(forms.Form):
    searchWords = forms.CharField(required=True)
