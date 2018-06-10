from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from . import models


@admin.register(models.Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    ordering = (
        '-id',
    )
    list_display = (
        'id',
        'adopter',
        'adopter_address',
        'adopter_phone',
        'recipient',
        'recipient_address',
        'status',
    )
    list_select_related = (
        'adopter',
        'adopter__street',
        'adopter__street__settlement',
        'recipient',
        'recipient__street',
        'recipient__street__settlement',
    )
    search_fields = (
        'adopter__user__first_name',
        'adopter__user__last_name',
        'recipient__first_name',
        'recipient__last_name',
    )
    list_filter = (
        'status',
    )
    list_editable = (
        'status',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
        'status_set_at',
    )
    fields = readonly_fields + (
        'status',
        # TODO: adopter and recipient should be readonly.
        'adopter',
        'recipient',
        'notes',
    )
    autocomplete_fields = (
        'adopter',
        'recipient',
    )

    def adopter_address(self, obj):
        return obj.adopter.address()
    adopter_address.short_description = _("Adopter's address")

    def adopter_phone(self, obj):
        return obj.adopter.phone
    adopter_phone.short_description = _("Adopter's phone")

    def recipient_address(self, obj):
        return obj.recipient.address()
    recipient_address.short_description = _("Recipient's address")


@admin.register(models.PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    ordering = (
        'name',
    )
    search_fields = (
        'name',
    )
    list_display = (
        'id',
        'name',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
    )
    fields = readonly_fields + (
        'name',
        'description',
    )


@admin.register(models.Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    ordering = (
        '-id',
    )
    list_display = (
        'id',
        'created_at',
        'delivery_from',
        'delivery_to',
        'status',
        'planned_delivery_date',
        'package_type',
    )
    list_editable = (
        'status',
    )
    list_filter = (
        'status',
    )
    list_select_related = (
        'delivery_from',
        'delivery_to',
        'package_type',
    )
    search_fields = (
        'delivery_from__user__first_name',
        'delivery_from__user__last_name',
        'delivery_to__first_name',
        'delivery_to__last_name',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
        'status_set_at',
    )
    fields = (
        'status',
        'delivery_from',
        'delivery_to',
        'planned_delivery_date',
        'package_type',
        'package_description',
        'delivery_description',
    )
    autocomplete_fields = (
        'delivery_from',
        'delivery_to',
    )
