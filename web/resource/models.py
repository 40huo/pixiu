from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from web.spider.models import Spider


def get_default_spider(self):
    """

    :return:
    """
    return Spider.objects.get(is_default=True)


# Create your models here.
@python_2_unicode_compatible
class Source(models.Model):
    """
    订阅源
    """
    name = models.CharField(verbose_name='名称', max_length=128)
    link = models.CharField(verbose_name='链接', max_length=512)
    description = models.TextField(verbose_name='描述', default='暂无')
    author = models.CharField(verbose_name='作者', max_length=64, default='Admin')
    spider_type = models.ForeignKey(to=Spider, verbose_name='爬虫类型', on_delete=models.SET_DEFAULT, default=get_default_spider)
    refresh_gap = models.PositiveSmallIntegerField(verbose_name='刷新间隔', max_length=10, default=60)
    # refresh_status =

    is_open = models.BooleanField(verbose_name='是否开启', default=True)
