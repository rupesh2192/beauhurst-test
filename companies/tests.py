# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .factories import CompanyFactory, EmployeeFactory, DealFactory, UserFactory
from .models import Company, Country
from .serializers import UserCompanyMaxEmpSerializer


class CompanyModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):  # noqa: N802
        cls.creator = User.objects.create(username='Me', email='me@example.com')
        cls.country = Country.objects.create(name='France', iso_code='fr')
        cls.company = Company.objects.create(
            name='A Company LTD',
            creator=cls.creator,
            date_founded=datetime.date(2019, 1, 1),
            country=cls.country,
            companies_house_id='LATEST'
        )
        CompanyFactory(date_founded=datetime.date(2018, 1, 1), companies_house_id='NEWEST')
        CompanyFactory(date_founded=datetime.date(2017, 1, 1), companies_house_id='MIDDLE')
        EmployeeFactory(company=cls.company)
        EmployeeFactory(company=cls.company)
        EmployeeFactory(company=cls.company)
        deal = DealFactory(company=cls.company, amount_raised=1000)

    def test_registration_date_cannot_be_in_future(self):
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self.company.date_founded = tomorrow
        with self.assertRaises(ValidationError):
            self.company.save()
        self.company.date_founded = datetime.date(2019, 1, 1)
        self.company.save()
        self.company.refresh_from_db()
        self.assertEqual(self.company.date_founded, datetime.date(2019, 1, 1))

    def test_start_monitoring(self):
        self.company.start_monitoring(self.creator)
        self.assertIn(self.creator, self.company.monitors.all())

    def test_recently_founded(self):
        companies = Company.recently_founded(limit=3)
        self.assertEqual(companies[0].companies_house_id, 'LATEST')
        self.assertEqual(companies[1].companies_house_id, 'NEWEST')
        self.assertEqual(companies[2].companies_house_id, 'MIDDLE')

    def test_quarter_wise(self):
        companies = Company.quarter_wise(year=20)
        companies = companies.order_by("founded_quarter")
        self.assertDictEqual(companies[0], {'founded_quarter': datetime.date(2017, 1, 1), 'companies': 1})
        self.assertDictEqual(companies[1], {'founded_quarter': datetime.date(2018, 1, 1), 'companies': 1})
        self.assertDictEqual(companies[2], {'founded_quarter': datetime.date(2019, 1, 1), 'companies': 1})

    def test_avg_employees(self):
        self.assertEqual(Company.avg_employees(), 1.0)

    def test_most_companies_created_by_user(self):
        self.assertEqual(Company.most_companies_created_by_user(), self.creator.username)

    def test_user_company_with_max_emp(self):
        companies = Company.user_company_with_max_emp()
        self.assertEqual(len(list(companies)), 1)
        companies = UserCompanyMaxEmpSerializer(companies, many=True).data
        self.assertDictEqual(companies[0], {
            "name": self.company.name,
            "id": self.company.id,
            "creator_id": self.company.creator.id,
            "username": self.company.creator.username,
            "emp_count": self.company.employee_set.count()
        })

    def test_country_avg_deal_amt(self):
        companies = Company.country_avg_deal_amt()
        self.assertEqual(companies.count(), 1)
        self.assertDictEqual(companies[0], {
            "country": self.country.id,
            "country__name": self.country.name,
            "avg_amt": 1000
        })


class CompanyAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.company = CompanyFactory()
        cls.user = UserFactory()

    def test_start_monitor(self):
        """
        Ensure authenticated user can start monitoring a company.
        """
        url = reverse('companies-monitor', args=[self.company.id])
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)
        response = self.client.patch(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check fetch monitors
        self.client.logout()
        url = reverse('companies-monitors')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exp = {
            "name": self.company.name,
            "companies_house_id": self.company.companies_house_id,
            "id": self.company.id,
            "date_founded": str(self.company.date_founded)
        }
        self.assertIn(exp, response.json())

    def test_stats(self):
        """
        Ensure stats API returns 200 with expected keys in the response.
        """
        url = reverse('companies-stats')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        exp = [
            "recently_founded",
            "quarter_wise",
            "avg_employees",
            "most_companies_created_by_user",
            "user_company_with_max_emp",
            "country_avg_deal_amt",
        ]
        self.assertListEqual(list(response.json().keys()), exp)

    def test_company_stats_view(self):
        url = reverse('companies-company-stats-view')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
