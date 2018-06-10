from django.db.models import Q, Max
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import list_route

from . import models
from . import serializers


class AdoptionResource(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    serializer_class = serializers.AdoptionSerializer

    class Meta:
        model = models.Adoption

    def get_queryset(self):
        queryset = models.Adoption.objects.filter(adopter_id=self.request.user.pk)
        return queryset

    @list_route(methods=['get'])
    def approved(self, request):
        queryset = models.Adoption.objects.filter(
            adopter_id=request.user.pk,
            status=models.Adoption.STATUS_APPROVED,
        ).annotate(
            last_delivery_at=Max(
                'recipient__deliveries__status_set_at',
                filter=Q(recipient__deliveries__status=models.Delivery.STATUS_DELIVERED),
            ),
        )
        serializer = serializers.ApprovedAdoptionSerializer(queryset, many=True)
        return Response(serializer.data)


class PackageResource(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    serializer_class = serializers.PackageTypeSerializer

    class Meta:
        model = models.PackageType

    def get_queryset(self):
        queryset = models.PackageType.objects.all()
        return queryset


class DeliveryResource(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    serializer_class = serializers.DeliverySerializer

    class Meta:
        model = models.Delivery

    def get_queryset(self):
        queryset = models.Delivery.objects.filter(delivery_from_id=self.request.user.pk)
        status = self.request.GET.get('status')
        for_adopted_recipients = self.request.GET.get('for_adopted_recipients')

        if for_adopted_recipients is not None:
            queryset = queryset.filter(
                delivery_to_id__in=models.Adoption.objects.filter(
                    adopter=self.request.user.pk,
                    status=models.Adoption.STATUS_APPROVED,
                ).values('recipient_id'),
            )

        if status is not None:
            queryset = queryset.filter(status=status)

        return queryset
