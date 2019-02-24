from rest_framework import serializers

from .models import Spider, SpiderEvent


class SpiderSerializer(serializers.ModelSerializer):
    """
    爬虫序列化
    """

    class Meta:
        model = Spider
        fields = '__all__'


class SpiderEventSerializer(serializers.ModelSerializer):
    """
    爬虫事件序列化
    """

    class Meta:
        model = SpiderEvent
        fields = '__all__'
