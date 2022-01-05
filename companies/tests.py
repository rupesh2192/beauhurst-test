# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import unittest

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .factories import CompanyFactory
from .models import Company, Country
from .views import most_recently_founded_companies


class CompanyModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa: N802
        creator = User.objects.create(username='Me', email='me@example.com')
        country = Country.objects.create(name='France', iso_code='fr')
        cls.company = Company.objects.create(
            name='A Company LTD',
            creator=creator,
            date_founded=datetime.date.today(),
            country=country,
        )

    @unittest.expectedFailure  # Feel free to implement validation
    def test_registration_date_cannot_be_in_future(self):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self.company.date_founded = tomorrow
        with self.assertRaises(ValidationError):
            self.company.save()


@pytest.mark.django_db
@pytest.mark.xfail  # Feel free to fix the bug
def test_most_recently_founded_companies():
    CompanyFactory(date_founded=datetime.date(2018, 1, 1), companies_house_id='NEWEST')
    CompanyFactory(date_founded=datetime.date(2016, 1, 1), companies_house_id='OLDEST')
    CompanyFactory(date_founded=datetime.date(2017, 1, 1), companies_house_id='MIDDLE')

    result = most_recently_founded_companies()
    chids = [comp['companies_house_id'] for comp in result]

    assert chids == ['NEWEST', 'MIDDLE', 'OLDEST']
