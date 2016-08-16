import uuid
from django.db import models


class CHCompany(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    company_number = models.CharField(
        max_length=8,
        null=False,
        blank=False,
        verbose_name="Company number")

    company_name = models.CharField(
        max_length=160,
        null=False,
        blank=False,
        verbose_name="Company name")

    registered_address_care_of = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Address care of")

    registered_address_po_box = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        verbose_name="Address POBox")

    registered_address_address_1 = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Address line 1 (House number and street")

    registered_address_address_2 = models.CharField(
        max_length=300,
        null=True,
        blank=True,
        verbose_name="Address line 2 (area)")

    registered_address_town = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Address town")

    registered_address_county = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Address county")

    registered_address_country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Address country")

    registered_address_postcode = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Address postcode")

    company_category = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Company category")

    company_status = models.CharField(
        max_length=70,
        null=True,
        blank=True,
        verbose_name="Company status")

    country_of_origin = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Country of origin")

    dissolution_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Dissolution date")

    incorporation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Incorporation date")

    accounts_accounting_ref_day = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Accounts accounting ref day")

    accounts_accounting_ref_month = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Accounts accounting ref month")

    accounts_next_due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Accounts next due date")

    accounts_last_made_up_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Accounts last made up date")

    accounts_category = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name="Accounts category",
        help_text="Accounts type description")

    returns_next_due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Returns next due date")

    returns_last_made_up_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Returns last made up date")

    mortgages_num_mort_charges = models.IntegerField(
        null=True,
        blank=True)

    mortgages_num_mort_outstanding = models.IntegerField(
        null=True,
        blank=True)

    mortgages_num_mort_part_satisfied = models.IntegerField(
        null=True,
        blank=True)

    mortgages_num_mort_satisfied = models.IntegerField(
        null=True,
        blank=True)

    sic_code_1 = models.CharField(
        max_length=170,
        null=True,
        blank=True)

    sic_code_2 = models.CharField(
        max_length=170,
        null=True,
        blank=True)

    sic_code_3 = models.CharField(
        max_length=170,
        null=True,
        blank=True)

    sic_code_4 = models.CharField(
        max_length=170,
        null=True,
        blank=True)

    limited_partnerships_num_gen_partners = models.IntegerField(
        null=True,
        blank=True)

    limited_partnerships_num_lim_partners = models.IntegerField(
        null=True,
        blank=True)

    uri = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    previous_name_1_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_1_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_2_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_2_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_3_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_3_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_4_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_4_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_5_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_5_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_6_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_6_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_7_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_7_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_8_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_8_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_9_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_9_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    previous_name_10_change_of_name_date = models.DateField(
        null=True,
        blank=True)

    previous_name_10_company_name = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    url = models.CharField(
        max_length=160,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = str(uuid.uuid4())
        models.Model.save(self, *args, **kwargs)