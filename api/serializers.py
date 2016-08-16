from rest_framework import serializers
from api.models import CHCompany


class CHCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = CHCompany
        fields = ('id', 'company_number', 'company_name')
