# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Avg, QuerySet
from django.db.models.functions import Trunc, Round
from django.utils import timezone
from model_utils.models import TimeStampedModel


class Country(models.Model):
    iso_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'{0}'.format(self.name)


class Company(TimeStampedModel):
    companies_house_id = models.CharField(max_length=8, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_founded = models.DateField(null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='companies_created'
    )
    monitors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='companies_monitored',
        help_text='Users who want to be notified of updates to this company'
    )

    def save(self, *args, **kwargs):
        if self.date_founded > timezone.now().date():
            raise ValidationError("Date founded must be a past date")
        return super(Company, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    def start_monitoring(self, user) -> None:
        """
        Adds the given user to the monitor list for the company
        :param user:
        :return:
        """
        self.monitors.add(user)

    @classmethod
    def recently_founded(cls, limit=10) -> QuerySet:
        """
        Returns queryset of the company containing `limit` (count) companies sorted in descending order by date_founded
        :param limit: no. of companies to be returned
        :return: Queryset of companies.
        """
        return cls.objects.order_by("-date_founded")[:limit]

    @classmethod
    def quarter_wise(cls, year=5) -> QuerySet:
        """
        Returns count of companies grouped by quarter in which they were formed in last `year` years.
        :param year: look back duration in years.
        :return: Queryset of Companies
        """
        temp = timezone.now().date()
        start_date = temp.replace(year=temp.year - year)
        return cls.objects.filter(date_founded__gte=start_date).annotate(
            founded_quarter=Trunc('date_founded', 'quarter')).values('founded_quarter').annotate(
            companies=Count('id'))

    @classmethod
    def avg_employees(cls) -> float:
        """
        Returns average count of employees for all companies.
        :return: Average count.
        """
        return round(Employee.objects.count() / cls.objects.count(), 2)

    @classmethod
    def most_companies_created_by_user(cls):
        """
        :return: Username of the user who has created most no. of companies.
        """
        temp = cls.objects.filter(creator__isnull=False).values("creator", "creator__username").annotate(c=Count("id")).order_by("-c")
        return temp[0].get("creator__username") if len(temp) > 0 else None

    @classmethod
    def user_company_with_max_emp(cls) -> QuerySet:
        """
        Returns Queryset of Company grouped by User with the greatest total number of employees at all companies
        they have created
        :return: Queryset
        """
        return Company.objects.raw("""select distinct on ("companies_company"."creator_id") creator_id , 
                    "au"."username","companies_company"."id", COUNT("companies_employee"."id") AS "emp_count" 
                    FROM "companies_company" LEFT OUTER JOIN "companies_employee" 
                    ON ("companies_company"."id" = "companies_employee"."company_id")
                    inner join auth_user au ON au.id=companies_company.creator_id
                    GROUP BY "companies_company"."id", "au"."username" HAVING COUNT("companies_employee"."id") > 0 
                    ORDER BY "creator_id", "emp_count" DESC""")

    @classmethod
    def country_avg_deal_amt(cls) -> QuerySet:
        """
        Average deal amount raised by country
        :return: Queryset of Companies with annotated column avg_amt.
        """
        return Company.objects.values("country", "country__name").annotate(
            avg_amt=Round(Avg("deal__amount_raised"), precision=2)).filter(avg_amt__gt=0)


class Deal(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_of_deal = models.DateField()
    amount_raised = models.FloatField()

    def __unicode__(self):
        return u'{0} raised by {1} ({2})'.format(
            self.amount_raised,
            self.company,
            self.date_of_deal
        )


class Employee(TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)

    GENDERS = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDERS)

    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('company', 'email')

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.company)
