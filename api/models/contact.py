import uuid
from django.db import models
from . import Company


class Contact(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Title")

    first_name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="First name")

    last_name = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="Last name")

    role = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Role")

    phone = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Phone")

    email = models.EmailField(null=True, blank=True)

    address_1 = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Address line 1 (House number and street")

    address_2 = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Address line 2 (area)")

    address_town = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Address town")

    address_county = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Address county")

    address_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Address country")

    address_postcode = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Address postcode")

    alt_phone = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Alt phone")

    alt_email = models.EmailField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    company = models.ForeignKey(
        to=Company,
        null=True,
        related_name="contacts")

    def __str__(self):
        return self.first_name + '' + self.last_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        models.Model.save(self, *args, **kwargs)