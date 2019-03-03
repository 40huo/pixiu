from django.db import models
from django.utils import timezone


def get_default_category():
    """
    返回默认的文章分类
    :return:
    """
    default, _ = ArticleCategory.objects.get_or_create(
        is_default=True,
        defaults={
            'name': '默认',
            'is_default': True
        }
    )
    return default.id


class ArticleCategory(models.Model):
    """
    文章分类
    """
    name = models.CharField(verbose_name='分类', max_length=64)
    is_default = models.BooleanField(verbose_name='是否默认分类', default=False)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '文章分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ArticleTag(models.Model):
    """
    文章标签
    """
    name = models.CharField(verbose_name='标签', max_length=64)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '文章标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Article(models.Model):
    """
    文章内容
    """
    from web.resource.models import Resource

    title = models.CharField(verbose_name='标题', max_length=256)
    url = models.CharField(verbose_name='原始地址', max_length=256)
    content = models.TextField(verbose_name='文章内容', blank=True)
    pub_time = models.DateTimeField(verbose_name='发布时间', default=timezone.now)
    category = models.ForeignKey(to=ArticleCategory, verbose_name='分类', on_delete=models.CASCADE, default=get_default_category)
    tag = models.ManyToManyField(to=ArticleTag, verbose_name='标签', blank=True)
    source = models.ForeignKey(to=Resource, verbose_name='订阅源', on_delete=models.CASCADE)
    hash = models.CharField(verbose_name='文章哈希', max_length=512, default='')
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        unique_together = ('title', 'hash')
