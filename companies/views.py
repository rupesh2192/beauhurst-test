# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import GenericViewError
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .models import Company
from .serializers import CompanySerializer, UserCompanyMaxEmpSerializer


class CompanyViewSet(GenericViewSet, ListModelMixin):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all()

    def get_permissions(self):
        if self.action in ["stats", "company_stats_view"]:
            return []
        return super(CompanyViewSet, self).get_permissions()

    @action(methods=["GET"], detail=False)
    def stats(self, request, **kwargs):
        return Response(data={})

    @action(methods=["PATCH"], detail=True)
    def monitor(self, request, **kwargs):
        instance = self.get_object()
        instance.start_monitoring(self.request.user)
        return Response(f"Started monitoring company {instance.name}")

    @action(methods=["GET"], detail=False)
    def monitors(self, request, **kwargs):
        queryset = self.serializer_class.Meta.model.objects.filter(monitors=self.request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["GET"], detail=False)
    def stats(self, request, **kwargs):
        model = self.serializer_class.Meta.model
        stats = {
            "recently_founded": self.serializer_class(model.recently_founded(), many=True).data,
            "quarter_wise": model.quarter_wise(),
            "avg_employees": model.avg_employees(),
            "most_companies_created_by_user": model.most_companies_created_by_user(),
            "user_company_with_max_emp": UserCompanyMaxEmpSerializer(model.user_company_with_max_emp(), many=True).data,
            "country_avg_deal_amt": model.country_avg_deal_amt(),
        }
        return Response(data=stats)

    @action(methods=["GET"], detail=False)
    def company_stats_view(self, request, **kwargs):
        return render(request, 'companies/company_stats.html')


