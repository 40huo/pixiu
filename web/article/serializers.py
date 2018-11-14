from rest_framework import serializers

from .models import Article, ArticleCategory


class ArticleCategorySerializer(serializers.ModelSerializer):
    """
    文章类别序列化
    """
    class Meta:
        model = ArticleCategory
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    """
    文章内容序列化
    """
    category = ArticleCategorySerializer()

    class Meta:
        model = Article
        fields = '__all__'
