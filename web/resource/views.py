from rest_framework import mixins
from rest_framework import viewsets

from .models import Resource, ResourceCategory
from .serializers import ResourceSerializer, ResourceCategorySerializer


# Create your views here.
class ResourceCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    订阅源分类
    """
    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer


class ResourceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    订阅源
    """
    queryset = Resource.objects.all().order_by('-updated')
    serializer_class = ResourceSerializer
