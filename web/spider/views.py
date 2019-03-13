from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Spider, SpiderEvent
from .serializers import SpiderSerializer, SpiderEventSerializer


# Create your views here.
class SpiderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    爬虫
    """
    queryset = Spider.objects.all().order_by('-updated')
    serializer_class = SpiderSerializer


class SpiderEventViewSet(viewsets.ModelViewSet):
    """
    爬虫事件
    """
    queryset = SpiderEvent.objects.all().order_by('-updated')
    serializer_class = SpiderEventSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
