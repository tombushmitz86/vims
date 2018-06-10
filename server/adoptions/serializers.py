import logging

from rest_framework import serializers
from . import models
from recipients.models import Recipient

logger = logging.getLogger('adoptions')


class AdoptionSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True)
    status_set_at = serializers.DateTimeField(read_only=True)
    recipient_uid = serializers.UUIDField(source='recipient.uid')
    recipient_background = serializers.CharField(source='recipient.background_story', read_only=True)
    recipient_tags = serializers.SerializerMethodField()

    class Meta:
        model = models.Adoption
        fields = (
            'id',
            'recipient_uid',
            'recipient_tags',
            'recipient_background',
            'status',
            'status_set_at',
        )

    def get_recipient_tags(self, obj):
        return ','.join(obj.recipient.recipient_tags)

    def create(self, validated_data):
        request = self.context['request']
        recipient_uid = validated_data.pop('recipient')['uid']

        try:
            recipient = Recipient.objects.get(uid=recipient_uid)
        except Recipient.DoesNotExist:
            logger.warning('Adoption request for not exists recipient uid: %s', recipient_uid)
            raise serializers.ValidationError('Recipient does not exists')

        if (
            self.Meta.model.objects.filter(
                recipient=recipient,
                status__in=[
                    self.Meta.model.STATUS_PENDING_APPROVAL,
                    self.Meta.model.STATUS_APPROVED,
                ]
            ).exclude(
                adopter_id=request.user.pk,
            ).exists()
        ):
            logger.warning('Adoption request for recipient uid: %s already exists', recipient_uid)
            raise serializers.ValidationError('Adoption request exists')

        adoption, created = self.Meta.model.objects.get_or_create(
            adopter_id=request.user.pk,
            recipient=recipient,
        )
        # Handle idempotency
        if not created:
            logger.warning('Adoption request for recipient uid: %s already exists', recipient_uid)

        return adoption


class ApprovedAdoptionSerializer(serializers.ModelSerializer):
    recipient_uid = serializers.UUIDField(source='recipient.uid', read_only=True)
    recipient_fullname = serializers.CharField(source='recipient.full_name', read_only=True)
    recipient_phone = serializers.CharField(source='recipient.phone', read_only=True)
    recipient_address = serializers.CharField(source='recipient.address', read_only=True)
    last_delivery_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = models.Adoption

        fields = (
            'recipient_uid',
            'recipient_fullname',
            'recipient_phone',
            'recipient_address',
            'status_set_at',
            'created_at',
            'last_delivery_at',
        )


class PackageTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PackageType
        fields = (
            'id',
            'name',
            'description',
        )


class DeliverySerializer(serializers.ModelSerializer):
    planned_delivery_date = serializers.DateField(read_only=True)
    delivery_to = serializers.UUIDField(label='delivery_to', source='delivery_to.uid')
    delivery_to_fullname = serializers.CharField(source='delivery_to.full_name', read_only=True)
    delivery_to_phone = serializers.CharField(source='delivery_to.phone', read_only=True)
    delivery_to_address = serializers.CharField(source='delivery_to.address', read_only=True)
    package_type_name = serializers.CharField(source='package_type.name', read_only=True)
    status_set_at = serializers.DateTimeField(
        format='%d/%m/%y',
        read_only=True,
    )

    def validate_status(self, value):
        if value not in (
            models.Delivery.STATUS_PENDING,
            models.Delivery.STATUS_DELIVERED,
        ):
            raise serializers.ValidationError('Invalid status %s for delivery' % value)

        return value

    class Meta:
        model = models.Delivery
        fields = (
            'id',
            'delivery_to',
            'delivery_to_fullname',
            'delivery_to_phone',
            'delivery_to_address',
            'planned_delivery_date',
            'status',
            'package_type',
            'package_type_name',
            'package_description',
            'delivery_description',
            'status_set_at',
        )

    def create(self, validated_data):
        request = self.context['request']
        recipient_uid = validated_data.pop('delivery_to')['uid']

        try:
            recipient = Recipient.objects.get(uid=recipient_uid)
        except Recipient.DoesNotExist:
            raise serializers.ValidationError('Recipient %s does not exists' % recipient_uid)

        return self.Meta.model.objects.create(
            delivery_from_id=request.user.pk,
            delivery_to=recipient,
            **validated_data,
        )

    def update(self, instance, validated_data):
        if instance.status not in (
            models.Delivery.STATUS_PLANNED,
            models.Delivery.STATUS_PENDING
        ):
            raise serializers.ValidationError('Delivery status: %s cannot be changed' % instance.status)

        instance.delivery_description = validated_data.get('delivery_description')
        instance.status = validated_data['status']
        instance.save()

        return instance
