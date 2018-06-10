import datetime

from django.urls import reverse
from django.core import mail
from django.utils import timezone

from ..models import Adoption, Delivery
from .base import TestAdoptionBase


class TestAdoption(TestAdoptionBase):
    DEFAULT = object()

    @classmethod
    def default(cls, value, default):
        return default if value is cls.DEFAULT else value

    @classmethod
    def request_adoption(
        cls,
        recipient_uid,
        client=DEFAULT,
    ):
        client = cls.default(client, cls.authenticated_client)
        return client.post(reverse('adoption-list'), {
            'recipient_uid': recipient_uid,
        })

    @classmethod
    def get_adoptions(
        cls,
        client=DEFAULT,
    ):
        client = cls.default(client, cls.authenticated_client)
        return client.get(reverse('adoption-list'))

    @classmethod
    def get_approved_adoptions(
        cls,
        client=DEFAULT,
    ):
        client = cls.default(client, cls.authenticated_client)
        return client.get(reverse('adoption-approved'))

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_should_request_adoption(self):
        response = self.request_adoption(recipient_uid=self.recipient.uid)

        assert response.status_code == 201
        assert response.data['status'] == Adoption.STATUS_PENDING_APPROVAL
        assert response.data['recipient_uid'] == str(self.recipient.uid)

    def test_should_get_adoptions(self):
        self.request_adoption(recipient_uid=self.recipient.uid)
        response = self.get_adoptions()

        adoption_request = response.data[0]
        assert adoption_request['recipient_uid'] == str(self.recipient.uid)
        assert adoption_request['recipient_background'] == self.recipient.background_story
        assert adoption_request['recipient_tags'] == ','.join(self.recipient.recipient_tags)
        assert adoption_request['status'] == Adoption.STATUS_PENDING_APPROVAL

    def test_should_get_approved_adoptions(self):
        response = self.request_adoption(recipient_uid=self.recipient.uid)

        adoption = Adoption.objects.get(id=response.data['id'])
        adoption.status = Adoption.STATUS_APPROVED
        adoption.save()

        response = self.get_approved_adoptions()

        data = response.data[0]
        assert data['recipient_uid'] == str(self.recipient.uid)
        assert data['recipient_fullname'] == self.recipient.full_name()
        assert data['recipient_phone'] == self.recipient.phone
        assert data['recipient_address'] == self.recipient.address()

    def test_should_get_approved_adoptions_with_last_delivery_date(self):
        response = self.request_adoption(recipient_uid=self.recipient.uid)

        adoption = Adoption.objects.get(id=response.data['id'])
        adoption.status = Adoption.STATUS_APPROVED
        adoption.save()

        response = self.get_approved_adoptions()
        data = response.data[0]
        assert data['last_delivery_at'] is None

        delivery = Delivery.objects.create(
            delivery_from=self.adopter.profile,
            delivery_to=self.recipient,
            status=Delivery.STATUS_DELIVERED,
        )
        delivery_status_at = timezone.get_default_timezone().localize(
            datetime.datetime(2018, 1, 1, 1, 1, 1),
        )
        delivery.status_set_at = delivery_status_at
        delivery.save()

        response = self.get_approved_adoptions()
        data = response.data[0]
        assert data['last_delivery_at'] == delivery_status_at.isoformat()

    def test_should_get_notified_on_status_changed(self):
        before_mailbox = len(mail.outbox)

        self.request_adoption(recipient_uid=self.recipient.uid)

        adoption = Adoption.objects.get(adopter=self.adopter.profile)
        adoption.status = Adoption.STATUS_APPROVED
        adoption.save()

        assert len(mail.outbox) == before_mailbox + 1

        adoption.status = Adoption.STATUS_REJECTED
        adoption.save()

        assert len(mail.outbox) == before_mailbox + 2

    def test_should_get_only_user_adoptions(self):
        self.request_adoption(recipient_uid=self.recipient.uid)

        response = self.get_adoptions(client=self.other_authenticated_client)

        assert len(response.data) == 0

    def test_should_idempotencly_request_adoption(self):
        response = self.request_adoption(
            recipient_uid=self.recipient.uid,
            client=self.authenticated_client,
        )

        assert response.status_code == 201
        adoption_id = response.data['id']

        response = self.request_adoption(
            recipient_uid=self.recipient.uid,
            client=self.authenticated_client,
        )
        assert response.data['id'] == adoption_id

    def test_should_not_request_adoption_on_existing_adoption_process_by_other_user(self):
        response = self.request_adoption(
            recipient_uid=self.recipient.uid,
            client=self.authenticated_client,
        )

        assert response.status_code == 201

        response = self.request_adoption(
            recipient_uid=self.recipient.uid,
            client=self.other_authenticated_client,
        )

        assert response.status_code == 400

    def test_should_not_request_adoption_if_anonymous_user(self):
        response = self.request_adoption(
            recipient_uid=self.recipient.uid,
            client=self.anonymous_client,
        )
        assert response.status_code == 401

    def test_should_not_get_adoptions_if_anonymous_user(self):
        response = self.get_adoptions(client=self.anonymous_client)
        assert response.status_code == 401
