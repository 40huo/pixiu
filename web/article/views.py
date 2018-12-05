from rest_framework import mixins
from rest_framework import viewsets

from .models import Article, ArticleCategory
from .serializers import ArticleSerializer, ArticleCategorySerializer


# Create your views here.
class ArticleListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    文章列表
    """
    queryset = Article.objects.all().order_by('-pub_time')
    serializer_class = ArticleSerializer


class ArticleCategoryListViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    文章分类
    """
    queryset = ArticleCategory.objects.all()
    serializer_class = ArticleCategorySerializer
