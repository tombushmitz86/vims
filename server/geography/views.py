from rest_framework import viewsets

from rest_framework.permissions import AllowAny
from . import models
from . import serializers


class SettlementResource(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.SettlementSerializer

    def get_queryset(self):
        queryset = models.Settlement.objects.all()
        q = self.request.query_params.get('q')

        if q is not None:
            return queryset.filter(name__contains=q)

        return queryset


class StreetResource(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.StreetSerializer

    def get_queryset(self):
        queryset = models.Street.objects.all()
        name = self.request.query_params.get('name')
        settlement_id = self.request.query_params.get('settlement_id')

        if name is not None:
            queryset = queryset.filter(name__contains=name)

        if settlement_id is not None:
            queryset = queryset.filter(settlement_id=settlement_id)

        return queryset
