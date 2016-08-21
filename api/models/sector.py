import uuid
from django.db import models
from . import Company


class Sector(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="title")

    company = models.ForeignKey(
        to=Company,
        null=True,
        related_name="sectors")