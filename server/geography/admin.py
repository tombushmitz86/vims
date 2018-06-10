from django.contrib import admin

from . import models


@admin.register(models.Settlement)
class SettlementAdmin(admin.ModelAdmin):
    ordering = (
        'name',
    )
    search_fields = (
        'name',
        'county_name',
        'municipality_name',
    )
    list_display = (
        'id',
        'name',
        'municipality_name',
        'county_name',
    )
    list_display_links = (
        'id',
        'name',
    )
    readonly_fields = (
        'created_at',
        'modified_at',
        'gov_id',
        'name',
        'county_gov_id',
        'county_name',
        'municipality_gov_id',
        'municipality_name',
    )
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.Street)
class StreetAdmin(admin.ModelAdmin):
    ordering = (
        'settlement__name',
        'name',
    )
    search_fields = (
        'settlement__name',
        'name',
    )
    list_display = (
        'id',
        'name',
        'settlement',
    )
    list_display_links = (
        'id',
        'name',
    )
    list_select_related = (
        'settlement',
    )
    readonly_fields = (
        'created_at',
        'modified_at',
        'settlement',
        'gov_id',
        'name',
    )
    fields = readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
