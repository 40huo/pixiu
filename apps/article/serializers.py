from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Article, ArticleCategory, ArticleTag


class ArticleTagSerializer(serializers.ModelSerializer):
    """
    文章标签序列化
    """

    class Meta:
        model = ArticleTag
        fields = '__all__'


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
    category = ArticleCategorySerializer(read_only=True)
    tag = ArticleTagSerializer(read_only=True)

    class Meta:
        model = Article
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Article.objects.all(),
                fields=('title', 'hash')
            )
        ]
