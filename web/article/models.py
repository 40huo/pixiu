# -*- coding: utf-8 -*-
# __author__ = '40huo'

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


# Create your models here.
@python_2_unicode_compatible
class ArticleCategory(models.Model):
    """
    文章分类
    """
    name = models.CharField(verbose_name='分类', max_length=64)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ArticleTag(models.Model):
    """
    文章标签
    """
    name = models.CharField(verbose_name='标签', max_length=64)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Article(models.Model):
    """
    文章内容
    """
    title = models.CharField(verbose_name='标题', max_length=256)
    url = models.CharField(verbose_name='原始地址', max_length=256)
    content = models.TextField(verbose_name='文章内容', blank=True)
    pub_time = models.DateTimeField(verbose_name='发布时间', default=timezone.now)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    category = models.ForeignKey(to=ArticleCategory, on_delete=models.CASCADE)
    tag = models.ManyToManyField(to=ArticleTag, blank=True)
    # source = models.ForeignKey(to=Source, )
