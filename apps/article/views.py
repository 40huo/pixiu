import datetime

from django.contrib.syndication.views import Feed
from django.utils import feedgenerator
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Article, ArticleCategory
from .serializers import ArticleSerializer, ArticleCategorySerializer
from ..resource.models import Resource


# Create your views here.
class ArticleViewSet(viewsets.ModelViewSet):
    """
    文章列表
    """
    queryset = Article.objects.prefetch_related('category', 'tag').all().order_by('-updated')
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (SessionAuthentication, TokenAuthentication,)


class ArticleCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    文章分类
    """
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ArticleFeed(Feed):
    """
    文章RSS
    """
    feed_type = feedgenerator.Atom1Feed

    def get_object(self, request, *args, **kwargs):
        source_name = kwargs.get('source_name', '')
        return Resource.objects.get(name=source_name)

    def title(self, obj):
        return obj.name

    def link(self, obj):
        return obj.link

    def description(self, obj):
        return obj.description

    def items(self, obj):
        return Article.objects.filter(source=obj).order_by('-pub_time')[:10]

    def item_link(self, item):
        return item.url

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return item.pub_time

    def item_description(self, item):
        return item.content

    def feed_copyright(self):
        return f'Copyright &copy; 2019-{datetime.date.today().year} Pixiu'
