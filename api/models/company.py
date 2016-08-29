import uuid
from django.db import models

from api.models import CHCompany


class Company(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company_number = models.CharField(
        max_length=8,
        null=False,
        blank=False,
        db_index=True,
        verbose_name="Company number")

    uk_based = models.BooleanField(
        null=False
    )

    business_type = models.CharField(
        max_length=160,
        null=False,
        blank=False,
        verbose_name="Business type")

    registered_name = models.CharField(
        max_length=160,
        null=False,
        blank=False,
        verbose_name="Registered name")

    trading_name = models.CharField(
        max_length=160,
        null=False,
        blank=False,
        verbose_name="Trading name")

    # sectors

    website = models.URLField(null=True, verbose_name="Website")

    number_of_employees = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Number of employees")

    annual_turnover = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Annual turnover")

    trading_address_1 = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Address line 1 (House number and street")

    trading_address_2 = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Address line 2 (area)")

    trading_address_town = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Address town")

    trading_address_county = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Address county")

    trading_address_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Address country")

    trading_address_postcode = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Address postcode")

    region = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Region")

    account_manager = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Account manger")

    currently_exporting = models.BooleanField()

    # countries of interest



    def __str__(self):
        return self.registered_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        models.Model.save(self, *args, **kwargs)
