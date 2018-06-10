import logging

from rest_framework import serializers

from . import models
from logistics.models import LogisticsCenter
from adoptions.serializers import DeliverySerializer


logger = logging.getLogger('activities')


class ActivityTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ActivityType
        fields = (
            'id',
            'description',
        )


class LogisticsCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticsCenter
        fields = (
            'id',
            'description',
            'address',
        )


class ActivityDaySerializer(serializers.ModelSerializer):
    logistics_center = LogisticsCenterSerializer()
    type = ActivityTypeSerializer()

    class Meta:
        model = models.ActivityDay
        fields = (
            'id',
            'date',
            'type',
            'logistics_center',
        )


class ActivityDayVolunteerSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        source='activity_day.date',
        read_only=True,
    )
    logistics_center = LogisticsCenterSerializer(
        source='activity_day.logistics_center',
        read_only=True,
    )
    activity_type = ActivityTypeSerializer(
        source='activity_day.type',
        read_only=True,
    )

    class Meta:
        model = models.ActivityDayVolunteer
        fields = (
            'activity_day',
            'date',
            'logistics_center',
            'activity_type',
        )

    def create(self, validated_data):
        request = self.context['request']

        activity, _ = self.Meta.model.objects.get_or_create(
            volunteer=request.user.profile,
            activity_day=validated_data['activity_day'],
        )

        return activity


class ActivityDayDeliverySerializer(serializers.ModelSerializer):
    """Serialize all deliveries which belongs to a activity day """

    delivery = DeliverySerializer(read_only=True)

    class Meta:
        model = models.ActivityDayDelivery
        fields = (
            'activity_day',
            'delivery',
        )
