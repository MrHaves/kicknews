# To create fixture ./manage.py dumpdata --format=xml --indent=4 -e contenttypes -e sessions -e auth.Permission -e tastypie.ApiKey > opennews/fixtures/initial_data.xml

import unicodedata

def cleanString(s):
	"""Removes all accents from the string"""
	if isinstance(s,str):
		s = unicode(s,"utf8","replace")
	s=unicodedata.normalize('NFD',s)
	return s.encode('ascii','ignore')
