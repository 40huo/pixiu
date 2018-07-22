from django.db import models
from django.utils import timezone


# Create your models here.
class Spider(models.Model):
    """

    """
    # 爬虫名称
    name = models.CharField(verbose_name='名称', max_length=128)
    # 爬虫描述
    description = models.TextField(verbose_name='描述', default='暂无')
    # 爬虫文件名
    filename = models.CharField(verbose_name='文件名', max_length=256)
    author = models.CharField(verbose_name='作者', max_length=32)
    create_time = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    update_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    is_enabled = models.BooleanField(verbose_name='是否启用', default=True)
    is_default = models.BooleanField(verbose_name='是否默认', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '爬虫'
        verbose_name_plural = verbose_name
