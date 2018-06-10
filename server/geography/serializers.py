from rest_framework import serializers

from . import models


class SettlementSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Settlement
        fields = (
            'id',
            'name',
            'county_name',
            'municipality_name',
        )


class StreetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Street
        fields = (
            'id',
            'settlement',
            'name',
        )
