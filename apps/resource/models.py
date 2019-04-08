from django.db import models
from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField


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
    REFRESH_STATUS_CHOICES = (
        (0, '从未刷新过'),
        (1, '刷新失败'),
        (2, '正在刷新'),
        (3, '上次刷新成功'),
    )

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

    category = models.ForeignKey(to=ResourceCategory, verbose_name='分类', on_delete=models.SET_NULL, blank=True, null=True)
    default_category = models.ForeignKey(ArticleCategory, verbose_name='文章默认分类', on_delete=models.SET_NULL, blank=True, null=True)
    default_tag = models.ForeignKey(ArticleTag, verbose_name='文章默认标签', on_delete=models.SET_NULL, blank=True, null=True)
    level = models.PositiveSmallIntegerField(verbose_name='等级', choices=RESOURCE_LEVEL_CHOICES)

    is_open = models.BooleanField(verbose_name='是否开启', default=True)
    is_deleted = models.BooleanField(verbose_name='是否删除', default=False)

    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '订阅源'
        verbose_name_plural = verbose_name
