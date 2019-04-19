from django.contrib import admin

from apps.spider.models import Proxy, Spider, SpiderEvent


# Register your models here.
@admin.register(Proxy)
class ProxyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Proxy._meta.fields]


@admin.register(SpiderEvent)
class SpiderEventAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SpiderEvent._meta.fields]


@admin.register(Spider)
class SpiderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Spider._meta.fields]
