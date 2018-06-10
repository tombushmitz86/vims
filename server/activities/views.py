from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from django.utils import timezone

from . import models
from . import serializers
from . import filters


def now():
    return timezone.now()


class ActivityTypeResource(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ActivityTypeSerializer
    queryset = models.ActivityType.objects.all()

    class Meta:
        model = models.ActivityType


class ActivityDayResource(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    permission_classes = (AllowAny,)
    serializer_class = serializers.ActivityDaySerializer
    filter_class = filters.ActivityDayFilter

    class Meta:
        model = models.ActivityDay

    def get_queryset(self):
        return models.ActivityDay.objects.filter(
            display_in_website=True,
            date__gte=now(),
        ).select_related(
            'type',
            'logistics_center',
            'logistics_center__street',
            'logistics_center__street__settlement',
        ).order_by('date')


class ActivityDayVolunteerResource(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = serializers.ActivityDayVolunteerSerializer
    filter_class = filters.ActivityDayVolunteerFilter

    class Meta:
        model = models.ActivityDayVolunteer

    def get_queryset(self):
        return models.ActivityDayVolunteer.objects.filter(
            volunteer_id=self.request.user.pk,
            active=True,
        )


class ActivityDayDeliveryResource(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = serializers.ActivityDayDeliverySerializer
    filter_class = filters.ActivityDayDeliveryFilter

    class Meta:
        model = models.ActivityDayDelivery

    def get_queryset(self):
        return models.ActivityDayDelivery.objects.filter(
            delivery__delivery_from_id=self.request.user.pk,
            active=True,
        )
