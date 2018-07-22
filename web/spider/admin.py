from django.contrib import admin

from web.spider.models import Spider


# Register your models here.
@admin.register(Spider)
class SpiderAdmin(admin.ModelAdmin):
    list_display = ('name', 'filename', 'author', 'is_enabled')
