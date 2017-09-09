from django.db import models
from django.utils.encoding import python_2_unicode_compatible


# Create your models here.
@python_2_unicode_compatible
class Intelligence(models.Model):
    """
    威胁情报内容
    """
    # 标题
    title = models.CharField('标题', max_length=256)
    # URL 地址
    url = models.CharField('地址', max_length=256)
    # 内容
    content = models.TextField('内容', blank=True)
    # 创建时间
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 修改时间
    last_modify_time = models.DateTimeField('修改时间', auto_now=True)
    # 分类
    category = models.ForeignKey(IntelligenceCategory)
    # 标签
    tag = models.ManyToManyField(IntelligenceTag, blank=True)

    class Meta:
        ordering = ['-create_time']
        verbose_name = '威胁情报'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class IntelligenceCategory(models.Model):
    """
    情报分类
    """
    name = models.CharField('分类', max_length=64)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class IntelligenceTag(models.Model):
    """
    情报标签
    """
    name = models.CharField('标签', max_length=64)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ResourceCategory(models.Model):
    """
    情报源分类
    """
    # 分类名称
    name = models.CharField('分类', max_length=64)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class IntelligenceResource(models.Model):
    """
    情报源
    """
    # 情报源地址
    url = models.CharField('地址', max_length=256)
    # 情报源标题
    title = models.CharField('标题', max_length=256)
    # 爬虫类型
    spider_type = models.IntegerField('爬虫类型')
    # 时间相关
    last_refresh_time = models.DateTimeField('上次刷新时间', auto_now=True)
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 分类
    category = models.ForeignKey(ResourceCategory)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Spider(models.Model):
    """
    爬虫类型
    """
    name = models.CharField
