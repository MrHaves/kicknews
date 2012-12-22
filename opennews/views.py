# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from opennews import models
from django.shortcuts import render_to_response,render
import datetime

def home(request):
	foo = datetime.datetime.now()
	return render(request, "index.html", locals())