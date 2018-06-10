from django.contrib import admin

from . import models


@admin.register(models.LogisticsCenter)
class LogisticsCenterAdmin(admin.ModelAdmin):
    ordering = (
        'description',
    )
    search_fields = (
        'description',
        'street__name',
        'street__settlement__name',
    )
    list_display = (
        'id',
        'description',
        'street',
        'street_number',
        'contact_person',
        'phone',
    )
    list_select_related = (
        'street',
        'street__settlement',
    )
    list_filter = (
        'street__settlement__county_name',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
    )
    fields = readonly_fields + (
        'description',
        'street',
        'street_number',
        'contact_person',
        'phone',
    )
    autocomplete_fields = (
        'street',
    )
