from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from adoptions.models import Adoption
from . import models
from . import serializers


class RecipientResource(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    serializer_class = serializers.RecipientSerializer

    def get_queryset(self):
        queryset = models.Recipient.objects.filter(
            active=True,
            blacklisted=False,
            display_in_website=True,

        ).select_related(
            'street',
            'street__settlement',
        )
        queryset = queryset.filter(
            # Filter only recipients which are not currently
            # in adoption/adoption request process.
            Q(adoptions=None) | Q(adoptions__status__in=(
                Adoption.STATUS_CANCELED,
                Adoption.STATUS_REJECTED,
            ))
        )

        query_tags = self.request.GET.get('tags')
        if query_tags is not None:
            query_tags = query_tags.split(',')
            queryset = queryset.filter(recipient_tags__overlap=query_tags)

        settlement_ids = self.request.GET.get('settlement_id')
        if settlement_ids is not None:
            settlement_ids = settlement_ids.split(',')
            queryset = queryset.filter(street__settlement_id__in=settlement_ids)

        return queryset
