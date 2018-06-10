import django_filters

from .models import (
    ActivityDay,
    ActivityDayDelivery,
    ActivityDayVolunteer,
)


class ActivityDayFilter(django_filters.FilterSet):
    from_date = django_filters.filters.DateFilter(
        field_name='date',
        lookup_expr='gte',
    )

    to_date = django_filters.filters.DateFilter(
        field_name='date',
        lookup_expr='lte',
    )

    class Meta:
        model = ActivityDay
        fields = (
            'from_date',
            'to_date',
            'type',
            'logistics_center',
        )


class ActivityDayVolunteerFilter(django_filters.FilterSet):
    from_date = django_filters.filters.DateFilter(
        field_name='activity_day__date',
        lookup_expr='gte',
    )
    to_date = django_filters.filters.DateFilter(
        field_name='activity_day__date',
        lookup_expr='lte',
    )

    class Meta:
        model = ActivityDayVolunteer
        fields = (
            'from_date',
            'to_date',
        )


class ActivityDayDeliveryFilter(django_filters.FilterSet):
    recipient_uid = django_filters.filters.UUIDFilter(
        field_name='delivery__delivery_to__uid',
    )
    package_type = django_filters.filters.NumberFilter(
        field_name='delivery__package_type',
    )
    description = django_filters.filters.CharFilter(
        field_name='delivery__delivery_description',
        lookup_expr='contains',
    )
    status = django_filters.filters.ChoiceFilter(
        field_name='delivery__status',
    )
    status_date = django_filters.filters.DateFilter(
        field_name='delivery__status_set_at',
    )

    class Meta:
        model = ActivityDayDelivery
        fields = (
            'recipient_uid',
            'package_type',
            'description',
            'status',
            'status_date',
        )
