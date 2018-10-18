from django.contrib import admin

from web.resource.models import ResourceCategory, Resource


# Register your models here.
@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'create_time', 'update_time', 'is_default')


@admin.register(Resource)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'author', 'spider_type', 'refresh_gap', 'refresh_status', 'last_refresh_time', 'category', 'level', 'is_open', 'is_deleted')
