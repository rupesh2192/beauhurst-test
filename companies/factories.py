import factory
from django.conf import settings
from django.utils.text import slugify

from .models import Company, Country, Deal, Employee


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: 'user{}'.format(n))
    email = email = factory.LazyAttribute(
        lambda user: '{}@example.com'.format(user.username)
    )
    password = factory.PostGenerationMethodCall('set_password', 'adm1n')


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('iso_code',)

    iso_code = factory.Faker('currency_code')
    name = factory.Faker('country')


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Faker('company')
    date_founded = factory.Faker('past_date')
    country = factory.SubFactory(CountryFactory)


class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal

    company = factory.SubFactory(CompanyFactory)
    date_of_deal = factory.Faker('past_date')
    amount_raised = factory.Faker('random_int', max=10000000)


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    company = factory.SubFactory(CompanyFactory)
    name = factory.Faker('name')
    job_title = factory.Faker('job')
    gender = factory.Faker(
        'random_element',
        elements=[gender[0] for gender in Employee.GENDERS]
    )
    email = factory.LazyAttribute(
        lambda employee: '{}@site.com'.format(slugify(employee.name))
    )
