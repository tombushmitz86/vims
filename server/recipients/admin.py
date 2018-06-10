from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.urls import reverse
from django.utils.html import format_html
from django import forms
from import_export import resources
from import_export.admin import ExportMixin

from adoptions.models import Delivery
from . import models


class RecipientResource(resources.ModelResource):
    class Meta:
        model = models.Recipient
        fields = (
            'created_at',
            'modified_at',
            'uid',
            'first_name',
            'last_name',
            'phone',
            'street',
            'street_number',
            'floor',
            'apartment',
            'background_story',
            'number_of_people',
            'recipient_tags',
            'display_in_website',
            'active',
            'blacklisted',
        )


# class RecipientTagsWidget(forms.SelectMultiple):
class RecipientTagsWidget(forms.CheckboxSelectMultiple):
    # I have no idea what this does, but it works.

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', models.Recipient.RECIPIENT_TAG_CHOICES)
        super().__init__(*args, **kwargs)

    def optgroups(self, name, value, attrs=None):
        selected = value[0].split(',') if value[0] else []
        subgroup = [
            self.create_option(name, v, label, v in selected, i)
            for (i, (v, label)) in enumerate(self.choices)
        ]
        return [(None, subgroup, 0)]

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        return ','.join(values)


class BlacklistedFilter(admin.SimpleListFilter):
    # Some ugliness to filter with default "No".

    title = _('Blacklisted')
    parameter_name = 'blacklisted'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
            ('no', _('No')),
            ('yes', _('Yes')),
        )

    def queryset(self, request, queryset):
        value = request.GET.get(self.parameter_name)
        if value == 'all':
            return queryset
        elif value == 'yes':
            return queryset.filter(blacklisted=True)
        return queryset.filter(blacklisted=False)

    def choices(self, cl):
        yield {
            'selected': self.value() is None,
            'query_string': cl.get_query_string({}, [self.parameter_name]),
            'display': _('No'),
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }


@admin.register(models.Recipient)
class RecipientAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = RecipientResource

    # Fine as long as there is only one ArrayField.
    formfield_overrides = {
        ArrayField: {'widget': RecipientTagsWidget},
    }

    def get_queryset(self, request):
        return super().get_queryset(request).with_last_delivery_at()

    ordering = (
        'last_name',
        'first_name',
    )
    search_fields = (
        'first_name',
        'last_name',
        'phone',
        'street__settlement__name',
    )
    list_display = (
        'id',
        'full_name',
        'address',
        'phone',
        'number_of_people',
        'deliveries_link',
        'last_delivery_at',
    )
    list_select_related = (
        'street',
        'street__settlement',
    )
    list_filter = (
        BlacklistedFilter,
        'street__settlement__county_name',
    )
    readonly_fields = (
        'created_at',
        'modified_at',
        'uid',
        'deliveries_link',
        'last_delivery_at',
    )
    fields = readonly_fields + (
        'first_name',
        'last_name',
        'phone',
        'street',
        'street_number',
        'floor',
        'apartment',
        'background_story',
        'number_of_people',
        'recipient_tags',
        'display_in_website',
        'active',
        'blacklisted',
    )
    autocomplete_fields = (
        'street',
    )

    def deliveries_link(self, obj):
        url = reverse('admin:{}_{}_changelist'.format(Delivery._meta.app_label, Delivery._meta.model_name))
        url = url + '?delivery_to={}'.format(obj.pk)
        return format_html('<a href="{}">{}</a>', url, self.deliveries_link.short_description)
    deliveries_link.short_description = _('Deliveries')

    def last_delivery_at(self, obj):
        return obj.last_delivery_at
    last_delivery_at.short_description = _('Last delivery at')
    last_delivery_at.admin_order_field = 'last_delivery_at'
