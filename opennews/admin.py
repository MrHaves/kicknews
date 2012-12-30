# -*- coding: utf-8 -*-
from django.contrib import admin
from opennews.models import *

admin.site.register(Member)
admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Comment)
admin.site.register(Media)