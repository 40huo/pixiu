# -*- coding: utf-8 -*-
# __author__ = '40huo'

from django.urls import path
from . import views

urlpatterns = [
    path('^$', views.index, name='index'),
]