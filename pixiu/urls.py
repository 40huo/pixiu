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
from rest_framework.authtoken.views import obtain_auth_token

from apps.article.views import ArticleViewSet, ArticleCategoryViewSet, ArticleFeed
from apps.resource.views import ResourceViewSet, ResourceCategoryViewSet
from apps.spider.views import SpiderViewSet, SpiderEventViewSet

router = routers.DefaultRouter()
router.register(r'article', ArticleViewSet, base_name="article")
router.register(r'article-category', ArticleCategoryViewSet, base_name="article-category")
router.register(r'resource', ResourceViewSet, base_name='resource')
router.register(r'resource-category', ResourceCategoryViewSet, base_name='resource-category')
router.register(r'spider', SpiderViewSet, base_name='spider')
router.register(r'spider-event', SpiderEventViewSet, base_name='spider-event')

urlpatterns = [
    path('api/', include(router.urls)),

    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('rss/<str:source_name>/', ArticleFeed())
]
