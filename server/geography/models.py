from django.db import models
from django.utils.translation import ugettext_lazy as _


class Settlement(models.Model):
    class Meta:
        verbose_name = _('Settlement')
        verbose_name_plural = _('Settlements')

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
    gov_id = models.IntegerField(
        verbose_name=_('Government ID'),
        unique=True,
    )
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100,
        unique=True,
    )
    county_gov_id = models.IntegerField(
        verbose_name=_('County government ID'),
    )
    county_name = models.CharField(
        verbose_name=_('County name'),
        max_length=100,
    )
    municipality_gov_id = models.IntegerField(
        verbose_name=_('Municipality government ID'),
    )
    municipality_name = models.CharField(
        verbose_name=_('Municipality name'),
        max_length=100,
    )

    def __str__(self):
        return self.name


class Street(models.Model):
    class Meta:
        verbose_name = _('Street')
        verbose_name_plural = _('Streets')
        unique_together = (
            ('settlement', 'gov_id'),
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
    settlement = models.ForeignKey(
        verbose_name=_('Settlement'),
        to=Settlement,
        on_delete=models.CASCADE,
    )
    gov_id = models.IntegerField(
        verbose_name=_('Government ID'),
    )
    name = models.CharField(
        verbose_name=_('Name'),
        max_length=100,
    )

    def __str__(self):
        return '{}//{}'.format(self.settlement.name, self.name)
