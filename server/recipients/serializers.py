from rest_framework import serializers

from . import models


class RecipientSerializer(serializers.ModelSerializer):
    settlement = serializers.PrimaryKeyRelatedField(
        source='street.settlement',
        read_only=True,
    )

    class Meta:
        model = models.Recipient
        fields = (
            'uid',
            'settlement',
            'recipient_tags',
            'background_story',
            'number_of_people',
        )
