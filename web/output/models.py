from django.db import models

from ..resource.models import Resource


# Create your models here.
class RSSOutput(models.Model):
    """
    RSS输出
    """
    filename = models.FileField(verbose_name='RSS文件地址', upload_to='output/')
    resource = models.ManyToManyField(verbose_name='对应订阅源', to=Resource)
    created = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = 'RSS输出'
        verbose_name_plural = verbose_name
