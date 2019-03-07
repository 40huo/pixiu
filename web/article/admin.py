from django.contrib import admin

from web.article.models import ArticleTag, ArticleCategory, Article


# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Article._meta.fields]


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ArticleCategory._meta.fields]


@admin.register(ArticleTag)
class ArticleTagAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ArticleTag._meta.fields]
