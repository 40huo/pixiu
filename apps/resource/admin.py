from django.contrib import admin

from .models import Authorization, ResourceCategory, Resource


# Register your models here.
@admin.register(Authorization)
class AuthorizationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Authorization._meta.fields]


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ResourceCategory._meta.fields]


@admin.register(Resource)
class SourceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resource._meta.fields]
