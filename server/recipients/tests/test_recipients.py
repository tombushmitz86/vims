from django.urls import reverse
from django.test import TestCase
from django.utils.http import urlencode
from rest_framework.test import APIClient

from ..models import Recipient
from geography.models import Street, Settlement
from users.models import User, UserProfile
from adoptions.models import Adoption


class TestRecipient(TestCase):
    DEFAULT = object()

    @classmethod
    def default(cls, value, default):
        return default if value is cls.DEFAULT else value

    @classmethod
    def get_recipients(
        cls,
        client=DEFAULT,
        tags=DEFAULT,
        settlement_id=DEFAULT,
    ):
        client = cls.default(client, cls.authenticated_client)

        tags = cls.default(tags, None)
        settlement_id = cls.default(settlement_id, None)

        q = {
            'tags': ','.join(tags) if tags is not None else None,
            'settlement_id': ','.join([str(id) for id in settlement_id]) if settlement_id is not None else None,
        }
        query = urlencode({k: v for k, v in q.items() if v is not None})

        return client.get('{}?{}'.format(reverse('recipient-list'), query))

    @classmethod
    def setUpTestData(cls):
        cls.anonymous_client = APIClient()
        cls.authenticated_client = APIClient()

        cls.user = User.objects.create(
            email='email@email.com',
            password='pass'
        )

        cls.authenticated_client.force_authenticate(user=cls.user)

        settlement = Settlement.objects.create(
            gov_id=1,
            name='settlement',
            county_gov_id=2,
            county_name='county name',
            municipality_gov_id=3,
            municipality_name='munic',
        )
        street = Street.objects.create(
            settlement=settlement,
            gov_id=2,
            name='street',
        )
        UserProfile.objects.create(
            user=cls.user,
            phone='999999999',
            street=street,
            street_number=2,
            floor=2,
            apartment=2,
            zipcode='99999',
        )
        cls.recipient = Recipient.objects.create(
            first_name='foo',
            last_name='bar',
            phone='999999999',
            street=street,
            street_number=2,
            floor=2,
            apartment=2,
            recipient_tags=[Recipient.RECIPIENT_TAG_SINGLE_PARENT],
            background_story='this is my background.',
            number_of_people=2,
        )
        Recipient.objects.create(
            first_name='foo2',
            last_name='bar2',
            phone='999999999',
            street=street,
            street_number=2,
            floor=2,
            apartment=2,
            recipient_tags=[
                Recipient.RECIPIENT_TAG_SINGLE_PARENT,
                Recipient.RECIPIENT_TAG_DOMESTIC_VIOLENCE,
            ],
            background_story='this is my background.',
            number_of_people=2,
        )

    def test_should_get_all_recipients(self):
        response = self.get_recipients()

        assert len(response.data) == 2

    def test_should_get_only_non_adopted_recipients(self):
        adoption = Adoption.objects.create(
            adopter=self.user.profile,
            recipient=self.recipient,
        )
        non_adopted_statuses = (
            Adoption.STATUS_REJECTED,
            Adoption.STATUS_CANCELED,
        )

        adopted_statuses = (
            Adoption.STATUS_PENDING_APPROVAL,
            Adoption.STATUS_APPROVED,
        )

        for adoption_status in non_adopted_statuses:
            with self.subTest(adoption_status=adoption_status):
                adoption.status = adoption_status
                adoption.save()
                response = self.get_recipients()
                assert len(response.data) == 2

        for adoption_status in adopted_statuses:
            with self.subTest(adoption_status=adoption_status):
                adoption.status = adoption_status
                adoption.save()
                response = self.get_recipients()
                assert len(response.data) == 1

    def test_should_get_only_filtered_recipients(self):
        response = self.get_recipients(
            tags=[Recipient.RECIPIENT_TAG_DOMESTIC_VIOLENCE],
        )

        assert len(response.data) == 1
        assert response.status_code == 200

        response = self.get_recipients(tags=[
            Recipient.RECIPIENT_TAG_DOMESTIC_VIOLENCE,
            Recipient.RECIPIENT_TAG_SINGLE_PARENT
        ])

        assert len(response.data) == 2
        assert response.status_code == 200

        response = self.get_recipients(
            settlement_id=[
                self.recipient.street.settlement_id,
            ]
        )

        assert len(response.data) == 2

        response = self.get_recipients(
            settlement_id=[
                9999,
            ],
        )

        assert len(response.data) == 0
