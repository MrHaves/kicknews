# -*- coding: utf-8 -*-
from django.contrib import admin
from opennews.models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import *

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Media)
admin.site.register(Member)

class MemberInline(admin.StackedInline):
    model = Member
    verbose_name_plural = 'profile'
   

# Define a new User admin
class UserAdmin(UserAdmin):
    inlines = (MemberInline, )	
    list_display   = ('username','email','is_staff')
    list_filter    = ('username', 'is_staff', 'is_active')
    ordering       = ('is_staff','is_active')
    search_fields  = ('username', 'email')
	
	
    # Configuration du formulaire d'édition
    fieldsets = (
    	# Fieldset 1 : Meta-info (titre, auteur...)
       ('Information', {
            'fields': ('username', 'email', 'password', 'is_staff')
        }),
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)