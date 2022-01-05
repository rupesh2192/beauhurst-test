# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stats/$', views.company_stats_api_view, name='company_stats_api_view'),
    url(r'^stats/view/$', views.company_stats_view, name='company_stats_view'),
]
