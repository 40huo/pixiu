from rest_framework import mixins
from rest_framework import viewsets

from .models import Spider
from .serializers import SpiderSerializer


# Create your views here.
class SpiderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    爬虫
    """
    queryset = Spider.objects.all().order_by('-updated')
    serializer_class = SpiderSerializer
