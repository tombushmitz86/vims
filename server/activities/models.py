from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.formats import date_format

from logistics.models import LogisticsCenter
from users.models import UserProfile
from adoptions.models import Delivery


class ActivityType(models.Model):
    class Meta:
        verbose_name = _('Activity type')
        verbose_name_plural = _('Activity types')

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

    def __str__(self):
        return self.description


class ActivityDay(models.Model):
    class Meta:
        verbose_name = _('Activity day')
        verbose_name_plural = _('Activity day')
        unique_together = (
            ('date', 'type', 'logistics_center'),
        )

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
    date = models.DateField(
        verbose_name=_('Date'),
    )
    type = models.ForeignKey(
        verbose_name=_('Type'),
        to=ActivityType,
        on_delete=models.PROTECT,
    )
    logistics_center = models.ForeignKey(
        verbose_name=_('Logistics center'),
        to=LogisticsCenter,
        on_delete=models.PROTECT,
    )
    display_in_website = models.BooleanField(
        verbose_name=_('Display in website'),
        default=True,
    )

    def __str__(self):
        return '{} - {}'.format(date_format(self.date), self.type)


class ActivityDayVolunteer(models.Model):
    class Meta:
        verbose_name = _('Activity day volunteer')
        verbose_name_plural = _('Activity days volunteers')
        unique_together = (
            ('volunteer', 'activity_day'),
        )

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
    activity_day = models.ForeignKey(
        verbose_name=_('Activity day'),
        to=ActivityDay,
        related_name='+',
        on_delete=models.CASCADE,
    )
    volunteer = models.ForeignKey(
        verbose_name=_('Volunteer'),
        to=UserProfile,
        related_name='+',
        on_delete=models.PROTECT,
    )
    active = models.BooleanField(
        verbose_name=_('Active'),
        default=True,
    )

    def __str__(self):
        return '{} - {}'.format(self.activity_day, self.volunteer)


class ActivityDayDelivery(models.Model):
    class Meta:
        verbose_name = _('Activity day delivery')
        verbose_name_plural = _('Activity days deliveries')
        unique_together = (
            ('activity_day', 'delivery'),
        )

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
    activity_day = models.ForeignKey(
        verbose_name=_('Activity day'),
        to=ActivityDay,
        related_name='+',
        on_delete=models.CASCADE,
    )
    delivery = models.ForeignKey(
        verbose_name=_('Delivery'),
        to=Delivery,
        related_name='+',
        on_delete=models.PROTECT,
    )
    active = models.BooleanField(
        verbose_name=_('Active'),
        default=True,
    )

    def __str__(self):
        return '{} - {}'.format(self.activity_day, self.delivery)
