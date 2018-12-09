from rest_framework import serializers

from web.spider.serializers import SpiderSerializer
from .models import Resource, ResourceCategory


class ResourceCategorySerializer(serializers.ModelSerializer):
    """
    订阅源类型序列化
    """

    class Meta:
        model = ResourceCategory
        fields = '__all__'


class ResourceSerializer(serializers.ModelSerializer):
    """
    订阅源序列化
    """
    category = ResourceCategorySerializer()
    spider_type = SpiderSerializer()

    class Meta:
        model = Resource
        fields = '__all__'
