from django.contrib import admin

from apps.resource.models import ResourceCategory, Resource


# Register your models here.
@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ResourceCategory._meta.fields]


@admin.register(Resource)
class SourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]