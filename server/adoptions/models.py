from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from users.models import UserProfile
from recipients.models import Recipient


class Adoption(models.Model):
    class Meta:
        verbose_name = _('Adoption')
        verbose_name_plural = _('Adoptions')
        unique_together = (
            'adopter',
            'recipient',
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

    adopter = models.ForeignKey(
        verbose_name=_('Adopter'),
        to=UserProfile,
        on_delete=models.PROTECT,
        related_name='adoptions',
    )
    recipient = models.ForeignKey(
        verbose_name=_('Recipient'),
        to=Recipient,
        on_delete=models.PROTECT,
        related_name='adoptions',
    )

    STATUS_PENDING_APPROVAL = 'PENDING_APPROVAL'
    STATUS_APPROVED = 'APPROVED'
    STATUS_REJECTED = 'DENIED'
    STATUS_CANCELED = 'CANCELED'
    STATUS_CHOICES = (
        (STATUS_PENDING_APPROVAL, _('Pending approval')),
        (STATUS_APPROVED, _('Approved')),
        (STATUS_REJECTED, _('Rejected')),
        (STATUS_CANCELED, _('Canceled')),
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING_APPROVAL,
    )
    # TODO: Currently updated by a DB trigger, find a better solution.
    status_set_at = models.DateTimeField(
        verbose_name=_('Status set at'),
        blank=True,
        auto_now_add=True,
    )

    notes = models.TextField(
        verbose_name=_('Notes'),
        blank=True,
    )

    def __str__(self):
        return _('Adoption %(pk)s') % {'pk': self.pk}


@receiver(post_save, sender=Adoption)
def send_mail_on_status_change(sender, instance, **kwargs):
    user_mail = instance.adopter.user.email
    from_mail = settings.DEFAULT_FROM_EMAIL

    if instance.status == Adoption.STATUS_APPROVED:
        subject = _('Adoption request approved')
        message = render_to_string('email/adoption_approved.html', {'adoption': instance})

    elif instance.status == Adoption.STATUS_REJECTED:
        subject = _('Adoption request rejected')
        message = render_to_string('email/adoption_rejected.html', {'adoption': instance})

    elif instance.status in (
        Adoption.STATUS_PENDING_APPROVAL,
        Adoption.STATUS_CANCELED,
    ):
        return
    else:
        assert False, 'Unhandled status: {}'.format(instance.status)

    mail = EmailMessage(subject=subject, body=message, to=[user_mail], from_email=from_mail)
    mail.content_subtype = 'html'
    mail.send()


class PackageType(models.Model):
    class Meta:
        verbose_name = _('Package type')
        verbose_name_plural = _('Package types')

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

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=70,
        unique=True,
    )
    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
    )

    def __str__(self):
        return self.name


class Delivery(models.Model):
    class Meta:
        verbose_name = _('Delivery')
        verbose_name_plural = _('Deliveries')
        # TODO: Unique constraints.

    id = models.AutoField(
        verbose_name=_('ID'),
        primary_key=True,
    )
    # created_at and modified_at are filled in at save().
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        blank=True,
        editable=False,
    )
    modified_at = models.DateTimeField(
        verbose_name=_('Modified at'),
        blank=True,
        editable=False,
    )

    delivery_from = models.ForeignKey(
        verbose_name=_('Delivery from'),
        to=UserProfile,
        on_delete=models.PROTECT,
        related_name='deliveries',
    )
    delivery_to = models.ForeignKey(
        verbose_name=_('Delivery to'),
        to=Recipient,
        on_delete=models.PROTECT,
        related_name='deliveries',
    )
    # defaults to creation date.
    planned_delivery_date = models.DateField(
        verbose_name=_('Planned delivery date'),
        blank=True,
    )
    package_type = models.ForeignKey(
        verbose_name=_('Package type'),
        to=PackageType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    package_description = models.TextField(
        verbose_name=_('Package description'),
        blank=True,
    )
    delivery_description = models.TextField(
        verbose_name=_('Delivery description'),
        blank=True,
    )

    STATUS_PLANNED = 'PLANNED'
    STATUS_PENDING = 'PENDING'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELED = 'CANCELED'
    STATUS_CHOICES = (
        (STATUS_PLANNED, _('Planned')),
        (STATUS_PENDING, _('Pending')),
        (STATUS_DELIVERED, _('Delivered')),
        (STATUS_CANCELED, _('Canceled')),
    )
    status = models.CharField(
        verbose_name=_('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PLANNED,
    )
    # TODO: Currently updated by a DB trigger, find a better solution.
    status_set_at = models.DateTimeField(
        verbose_name=_('Status set at'),
        blank=True,
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        now = timezone.now()
        self.modified_at = now
        if self.pk is None:
            self.created_at = now
            if self.planned_delivery_date is None:
                # Assumes local timezone.
                self.planned_delivery_date = now.date()
        super().save(*args, **kwargs)

    def __str__(self):
        return _('Delivery %(pk)s') % {'pk': self.pk}
