from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.abstract_models import AbstractTimestampedModel, AbstractSoftDeleteModel, TitleField


class Country(AbstractTimestampedModel, AbstractSoftDeleteModel):
    name = TitleField()
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    def __str__(self):
        return f"{self.name} [#{self.id}]"


class City(AbstractTimestampedModel, AbstractSoftDeleteModel):
    name = TitleField()
    code = models.CharField(max_length=10, unique=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def __str__(self):
        return f"{self.name}, {self.country} [#{self.id}]"
