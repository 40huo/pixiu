# -*- coding: utf-8 -*-
# __author__ = '40huo'

"""pixiu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from web.article.views import ArticleViewSet, ArticleCategoryViewSet
from web.resource.views import ResourceViewSet, ResourceCategoryViewSet
from web.spider.views import SpiderViewSet

router = routers.DefaultRouter()
router.register(r'article', ArticleViewSet, base_name="article")
router.register(r'article-category', ArticleCategoryViewSet, base_name="article-category")
router.register(r'resource', ResourceViewSet, base_name='resource')
router.register(r'resource-category', ResourceCategoryViewSet, base_name='resource-category')
router.register(r'spider', SpiderViewSet, base_name='spider')

urlpatterns = [
    path('api/', include(router.urls)),

    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
