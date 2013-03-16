import unicodedata

def cleanString(s):
	"""Removes all accents from the string"""
	if isinstance(s,str):
		s = unicode(s,"utf8","replace")
	s=unicodedata.normalize('NFD',s)
	return s.encode('ascii','ignore')
