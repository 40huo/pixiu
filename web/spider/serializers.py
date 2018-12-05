from rest_framework import serializers

from .models import Spider


class SpiderSerializer(serializers.ModelSerializer):
    """
    爬虫序列化
    """

    class Meta:
        model = Spider
        fields = '__all__'
