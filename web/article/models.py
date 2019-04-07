from django.db import models
from django.utils import timezone
from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField


class ArticleCategory(models.Model):
    """
    文章分类
    """
    name = models.CharField(verbose_name='分类', max_length=64)
    is_default = models.BooleanField(verbose_name='是否默认分类', default=False)
    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

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
    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

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
    url = models.URLField(verbose_name='原始地址', max_length=256)
    content = models.TextField(verbose_name='文章内容', blank=True)
    pub_time = models.DateTimeField(verbose_name='发布时间', default=timezone.now)
    category = models.ForeignKey(to=ArticleCategory, verbose_name='分类', on_delete=models.SET_NULL, blank=True, null=True)
    tag = models.ManyToManyField(to=ArticleTag, verbose_name='标签', blank=True)
    source = models.ForeignKey(to=Resource, verbose_name='订阅源', on_delete=models.CASCADE)
    hash = models.CharField(verbose_name='文章哈希', max_length=512, default='')
    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        unique_together = ('title', 'hash')
