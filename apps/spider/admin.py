from django.contrib import admin

from apps.spider.models import Spider


# Register your models here.
@admin.register(Spider)
class SpiderAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Spider._meta.fields]
