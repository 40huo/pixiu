# -*- coding: utf-8 -*-
# __author__ = '40huo'

from django.conf.urls import url
from web.reader import views

urlpatterns = [
    url('^$', views.index, name='index'),
]