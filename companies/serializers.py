from rest_framework import serializers

from companies.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("name", "companies_house_id", "id", "date_founded")


class UserCompanyMaxEmpSerializer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()
    creator_id = serializers.IntegerField()
    username = serializers.SlugField()
    emp_count = serializers.IntegerField()
