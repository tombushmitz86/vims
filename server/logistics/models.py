from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from geography.models import Street


class LogisticsCenter(models.Model):
    class Meta:
        verbose_name = _('Logistics center')
        verbose_name_plural = _('Logistics centers')

    id = models.AutoField(
        verbose_name=_('ID'),
        primary_key=True,
    )
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
        blank=True,
    )
    modified_at = models.DateTimeField(
        verbose_name=_('Modified at'),
        auto_now=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name=_('Description'),
        unique=True,
    )
    street = models.ForeignKey(
        verbose_name=_('Street'),
        to=Street,
        on_delete=models.PROTECT,
        related_name='logistics_centers',
    )
    street_number = models.IntegerField(
        verbose_name=_('Street number'),
    )
    contact_person = models.CharField(
        verbose_name=_('Contact person'),
        max_length=150,
        blank=True,
        null=True,
    )
    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=25,
        validators=[
            RegexValidator(r'^[0-9() -]{6,25}$'),
        ],
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.description

    def address(self):
        return _('{settlement_name}, {street_number} {street_name}').format(
            settlement_name=self.street.settlement.name,
            street_number=self.street_number,
            street_name=self.street.name,
        )
    address.short_description = _('Address')
