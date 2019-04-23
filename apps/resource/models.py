from django.db import models
from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField

from utils import enums
from ..spider.models import Proxy


class Authorization(models.Model):
    """
    认证
    """
    AUTH_TYPE_CHOICES = (
        (0, '账号'),
        (1, 'Cookie'),
        (2, '请求头')
    )
    name = models.CharField(verbose_name='认证名称', max_length=64)
    type = models.PositiveSmallIntegerField(verbose_name='认证类型', choices=AUTH_TYPE_CHOICES, default=0)
    username = models.CharField(verbose_name='账号', max_length=128, default='', blank=True)
    password = models.CharField(verbose_name='密码', max_length=128, default='', blank=True)
    cookie = models.CharField(verbose_name='Cookie', max_length=512, default='', blank=True)
    auth_header = models.CharField(verbose_name='认证请求头', max_length=128, default='', blank=True)
    auth_value = models.CharField(verbose_name='认证Token', max_length=128, default='', blank=True)
    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '认证'
        verbose_name_plural = verbose_name


class ResourceCategory(models.Model):
    """
    订阅源分类
    """
    name = models.CharField(verbose_name='分类名称', max_length=64)
    description = models.TextField(verbose_name='描述', default='暂无')
    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '订阅源分类'
        verbose_name_plural = verbose_name


class Resource(models.Model):
    """
    订阅源
    """
    from apps.spider.models import Spider
    from apps.article.models import ArticleCategory, ArticleTag

    # 刷新状态
    REFRESH_STATUS_CHOICES = enums.ResourceRefreshStatus.choices()

    RESOURCE_LEVEL_CHOICES = (
        (0, '公开'),
        (1, '个人'),
        (2, '保密'),
        (3, '绝密'),
    )

    name = models.CharField(verbose_name='名称', max_length=128)
    link = models.URLField(verbose_name='链接', max_length=512)
    description = models.TextField(verbose_name='描述', default='暂无')
    author = models.CharField(verbose_name='作者', max_length=64, default='Admin')
    spider_type = models.ForeignKey(to=Spider, verbose_name='爬虫类型', on_delete=models.SET_NULL, blank=True, null=True)
    refresh_gap = models.PositiveSmallIntegerField(verbose_name='刷新间隔', default=60)  # 单位 小时
    refresh_status = models.PositiveSmallIntegerField(verbose_name='刷新状态', choices=REFRESH_STATUS_CHOICES)
    last_refresh_time = models.DateTimeField(verbose_name='上次刷新时间')
    auth = models.ForeignKey(to=Authorization, verbose_name='认证', on_delete=models.SET_NULL, blank=True, null=True)
    proxy = models.ForeignKey(to=Proxy, verbose_name='代理', on_delete=models.SET_NULL, blank=True, null=True)

    category = models.ForeignKey(to=ResourceCategory, verbose_name='分类', on_delete=models.SET_NULL, blank=True, null=True)
    default_category = models.ForeignKey(ArticleCategory, verbose_name='文章默认分类', on_delete=models.SET_NULL, blank=True, null=True)
    default_tag = models.ForeignKey(ArticleTag, verbose_name='文章默认标签', on_delete=models.SET_NULL, blank=True, null=True)
    level = models.PositiveSmallIntegerField(verbose_name='等级', choices=RESOURCE_LEVEL_CHOICES)

    is_enabled = models.BooleanField(verbose_name='是否开启', default=True)
    is_deleted = models.BooleanField(verbose_name='是否删除', default=False)

    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '订阅源'
        verbose_name_plural = verbose_name
