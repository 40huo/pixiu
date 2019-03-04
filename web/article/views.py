from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Article, ArticleCategory
from .serializers import ArticleSerializer, ArticleCategorySerializer


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
