from rest_framework import mixins
from rest_framework import viewsets

from .models import Spider, SpiderEvent
from .serializers import SpiderSerializer, SpiderEventSerializer


# Create your views here.
class SpiderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    爬虫
    """
    queryset = Spider.objects.all().order_by('-updated')
    serializer_class = SpiderSerializer


class SpiderEventViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    爬虫事件
    """
    queryset = SpiderEvent.objects.all().order_by('-updated')
    serializer_class = SpiderEventSerializer
