# -*- coding: utf-8 -*-
# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from opennews import models
from django.shortcuts import render_to_response,render

def home(request):
	foo = "bip"
	return render(request, "index.html", locals())