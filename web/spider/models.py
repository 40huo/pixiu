from django.db import models
from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField


class Spider(models.Model):
    """
    爬虫
    """
    name = models.CharField(verbose_name='名称', max_length=128)
    description = models.TextField(verbose_name='描述', default='暂无')
    filename = models.CharField(verbose_name='文件名', max_length=256)
    author = models.CharField(verbose_name='作者', max_length=32)
    is_enabled = models.BooleanField(verbose_name='是否启用', default=True)
    is_default = models.BooleanField(verbose_name='是否默认', default=False)

    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '爬虫'
        verbose_name_plural = verbose_name


class SpiderEvent(models.Model):
    """
    爬虫事件
    """
    MESSAGE_LEVEL_CHOICE = (
        (0, 'DEBUG'),
        (1, 'INFO'),
        (2, 'WARNING'),
        (3, 'ERROR'),
        (4, 'CRITICAL')
    )

    spider = models.ForeignKey(Spider, on_delete=models.CASCADE, verbose_name='爬虫')
    message = models.TextField(verbose_name='事件信息', default='')
    level = models.IntegerField(verbose_name='事件等级', choices=MESSAGE_LEVEL_CHOICE)
    created = CreationDateTimeField(verbose_name='创建时间')
    updated = ModificationDateTimeField(verbose_name='更新时间')

    class Meta:
        verbose_name = '爬虫事件'
        verbose_name_plural = verbose_name
