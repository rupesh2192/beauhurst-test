# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
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

    def __unicode__(self):
        return u'{0}'.format(self.name)


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
