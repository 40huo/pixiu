from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Resource, ResourceCategory
from .serializers import ResourceSerializer, ResourceCategorySerializer


# Create your views here.
class ResourceCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    订阅源分类
    """
    queryset = ResourceCategory.objects.all()
    serializer_class = ResourceCategorySerializer


class ResourceViewSet(viewsets.ModelViewSet):
    """
    订阅源
    """
    queryset = Resource.objects.select_related('category').all().order_by('-updated')
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication, TokenAuthentication,)
