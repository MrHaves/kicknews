"""
We begin by creating a sim indexes returning articles on Article (body, title, tags ...), Geolocation data, ...
"""

from haystack import indexes
from opennews.models import *
from tools import *

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    tags = indexes.CharField()
    date   = indexes.DateTimeField(model_attr='date')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, object):
        """  """
        self.prepared_data = super(ArticleIndex, self).prepare(object)
        self.prepared_data['tags'] = [tag.tag for tag in object.tags.all()]
        self.prepared_data['text'] += '\n' + cleanString(self.prepared_data['text'])
        return self.prepared_data

class FeedEntryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    date   = indexes.DateTimeField(model_attr='date')

    def get_model(self):
        return FeedEntry

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, object):
        """  """
        self.prepared_data = super(FeedEntryIndex, self).prepare(object)
        self.prepared_data['text'] += '\n' + cleanString(self.prepared_data['text'])
        return self.prepared_data