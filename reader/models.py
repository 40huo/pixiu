from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# Create your models here.
@python_2_unicode_compatible
class Intelligence(models.Model):
    """
    威胁情报内容
    """
    title = models.CharField('标题', max_length=256)
    url = models.CharField('地址', max_length=256)
    content = models.TextField('内容', blank=True)
    description = models.TextField('描述', blank=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['-create_time']
        verbose_name = '威胁情报'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    分类
    """
    pass


class IntelligenceResource(models.Model):
    """
    情报源
    """
    # 情报源地址
    url = models.CharField('地址', max_length=256)
    # 情报源标题
    title = models.CharField('标题', max_length=256)
    # 情报源描述
    description = models.TextField('描述', blank=True)
    # 爬虫类型
    spider_type = models.IntegerField('爬虫类型')
    # 时间相关
    last_refresh_time = models.DateTimeField('上次刷新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now_add=True)
