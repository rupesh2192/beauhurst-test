# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Company, Country, Deal, Employee


class EmployeeCountListFilter(admin.SimpleListFilter):
    title = 'Number of employees'
    parameter_name = 'n_employees'

    def lookups(self, request, model_admin):
        return (
            (1, 'at least 1'),
            (3, 'at least 3'),
            (5, 'at least 5'),
            (10, 'at least 10'),
        )

    def queryset(self, request, queryset):
        # NOTE: this runs really slow in production once we've got a full DB
        if not self.value():
            pks = queryset.values_list('pk', flat=True)
        else:
            pks = []
            for company in queryset:
                if company.employee_set.count() >= int(self.value()):
                    pks.append(company.pk)

        return queryset.filter(pk__in=pks)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_filter = ('date_founded', EmployeeCountListFilter,)


admin.site.register(Country)
admin.site.register(Deal)
admin.site.register(Employee)
