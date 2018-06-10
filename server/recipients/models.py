import uuid

from django.db import models
from django.db.models import Q, Max
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from geography.models import Street


class RecipientQuerySet(models.QuerySet):
    def with_last_delivery_at(self):
        # Import here to avoid circular dependency.
        from adoptions.models import Delivery

        return self.annotate(
            last_delivery_at=Max(
                'deliveries__status_set_at',
                filter=Q(deliveries__status=Delivery.STATUS_DELIVERED),
            ),
        )


class Recipient(models.Model):
    class Meta:
        verbose_name = _('Recipient')
        verbose_name_plural = _('Recipients')

    id = models.AutoField(
        verbose_name=_('ID'),
        primary_key=True,
    )
    uid = models.UUIDField(
        verbose_name=_('ID'),
        unique=True,
        default=uuid.uuid4,
        editable=False,
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
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=30,
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=30,
    )
    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=25,
        validators=[
            RegexValidator(r'^[0-9() -]{6,25}$'),
        ],
    )
    street = models.ForeignKey(
        verbose_name=_('Street'),
        to=Street,
        on_delete=models.PROTECT,
        related_name='recipients',
    )
    street_number = models.IntegerField(
        verbose_name=_('Street number'),
    )
    floor = models.SmallIntegerField(
        verbose_name=_('Floor'),
    )
    apartment = models.IntegerField(
        verbose_name=_('Apartment'),
    )
    background_story = models.TextField(
        verbose_name=_('Background story'),
        blank=True,
    )
    number_of_people = models.PositiveSmallIntegerField(
        verbose_name=_('Number of people'),
        blank=True,
        null=True,
    )

    objects = RecipientQuerySet.as_manager()

    RECIPIENT_TAG_1 = 'family'
    RECIPIENT_TAG_2 = 'single-person'
    RECIPIENT_TAG_CHOICES = (
        (RECIPIENT_TAG_1, _('Family')),
        (RECIPIENT_TAG_2, _('Single Person')),
    )
    recipient_tags = ArrayField(
        verbose_name=_('Recipient tags'),
        base_field=models.CharField(
            verbose_name=_('Recipient tag'),
            max_length=30,
            choices=RECIPIENT_TAG_CHOICES,
        ),
    )

    display_in_website = models.BooleanField(
        verbose_name=_('Display in website'),
        default=True,
    )
    active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
    )
    blacklisted = models.BooleanField(
        verbose_name=_('Blacklisted'),
        default=False,
    )

    def short_name(self):
        return self.first_name
    short_name.short_description = _('Short name')

    def full_name(self):
        return (self.first_name + ' ' + self.last_name).strip()
    full_name.short_description = _('Full name')

    def address(self):
        return _('{settlement_name}, {street_number} {street_name}, apt. {apartment}, floor {floor}').format(
            settlement_name=self.street.settlement.name,
            street_number=self.street_number,
            street_name=self.street.name,
            apartment=self.apartment,
            floor=self.floor,
        )
    address.short_description = _('Address')

    def __str__(self):
        return self.full_name()
