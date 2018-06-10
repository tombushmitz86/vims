from django.contrib import admin

from . import models


@admin.register(models.ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    ordering = (
        'description',
    )
    search_fields = (
        'description',
    )
    list_display = (
        'id',
        'description',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
    )
    fields = readonly_fields + (
        'description',
    )


@admin.register(models.ActivityDay)
class ActivityDayAdmin(admin.ModelAdmin):
    ordering = (
        'date',
        'type',
        'logistics_center',
    )
    search_fields = (
        'description',
    )
    list_display = (
        'id',
        'date',
        'type',
        'logistics_center',
        'display_in_website',
    )
    list_select_related = (
        'type',
        'logistics_center',
    )
    list_filter = (
        'type',
        'logistics_center',
    )
    list_editable = (
        'display_in_website',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
    )
    fields = readonly_fields + (
        'date',
        'type',
        'logistics_center',
        'display_in_website',
    )


@admin.register(models.ActivityDayVolunteer)
class ActivityDayVolunteerAdmin(admin.ModelAdmin):
    ordering = (
        '-activity_day',
        'volunteer',
    )
    list_display = (
        'activity_day',
        'volunteer',
        'active',
    )
    list_editable = (
        'active',
    )
    list_select_related = (
        'activity_day',
        'activity_day__type',
        'volunteer',
        'volunteer__user',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
    )
    fields = readonly_fields + (
        'activity_day',
        'volunteer',
        'active',
    )
    autocomplete_fields = (
        'volunteer',
    )


@admin.register(models.ActivityDayDelivery)
class ActivityDayDeliveryAdmin(admin.ModelAdmin):
    ordering = (
        '-activity_day',
        'delivery',
    )
    list_display = (
        'activity_day',
        'delivery',
        'active',
    )
    list_editable = (
        'active',
    )
    list_select_related = (
        'activity_day',
        'activity_day__type',
        'delivery',
    )
    readonly_fields = (
        'id',
        'created_at',
        'modified_at',
    )
    fields = readonly_fields + (
        'activity_day',
        'delivery',
        'active',
    )
