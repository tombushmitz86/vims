import datetime

from django.urls import reverse
from urllib.parse import urlencode

from ..models import PackageType, Delivery, Adoption
from .base import TestAdoptionBase


class TestDelivery(TestAdoptionBase):
    DEFAULT = object()

    @classmethod
    def default(cls, value, default):
        return default if value is cls.DEFAULT else value

    @classmethod
    def get_deliveries(
        cls,
        client=DEFAULT,
        status=DEFAULT,
        for_adopted_recipients=DEFAULT,
    ):
        client = cls.default(client, cls.authenticated_client)
        status = cls.default(status, None)
        for_adopted_recipients = cls.default(for_adopted_recipients, None)

        params = {
            'status': status,
            'for_adopted_recipients': for_adopted_recipients,
        }

        params = urlencode({k: v for k, v in params.items() if v is not None})

        return client.get('{}?{}'.format(
            reverse('delivery-list'),
            params,
        ))

    @classmethod
    def create_delivery(
        cls,
        client=DEFAULT,
        package_type=DEFAULT,
        delivery_to=DEFAULT,
        delivery_description=DEFAULT,
        package_description=DEFAULT,
        status=DEFAULT,
    ):
        client = cls.default(client, cls.authenticated_client)
        package_type = cls.default(package_type, cls.package_type)
        delivery_to = cls.default(delivery_to, cls.recipient)
        delivery_description = cls.default(delivery_description, '')
        package_description = cls.default(package_description, '')
        status = cls.default(status, Delivery.STATUS_DELIVERED)

        return client.post(reverse('delivery-list'), {
            'package_type': package_type.id,
            'delivery_to': delivery_to.uid,
            'delivery_description': delivery_description,
            'package_description': package_description,
            'status': status,
        })

    @classmethod
    def update_delivery(
        cls,
        delivery_id,
        client=DEFAULT,
        status=DEFAULT,
        delivery_description=DEFAULT,
    ):
        client = cls.default(client, cls.authenticated_client)
        delivery_description = cls.default(delivery_description, '')
        status = cls.default(status, Delivery.STATUS_DELIVERED)

        return client.patch(reverse('delivery-detail', args=(delivery_id, )), {
            'delivery_description': delivery_description,
            'status': status,
        })

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.asof = datetime.date(1947, 1, 1)

        cls.package_type = PackageType.objects.create(
            name='package',
            description='description',
        )
        cls.delivery = Delivery.objects.create(
            delivery_from=cls.adopter.profile,
            delivery_to=cls.recipient,
            package_type=cls.package_type,
            planned_delivery_date=cls.asof,
            package_description='',
            delivery_description='',
        )

    def test_should_get_all_user_deliveries(self):
        response = self.get_deliveries()
        delivery = response.data[0]

        assert delivery['delivery_to'] == str(self.recipient.uid)
        assert delivery['delivery_to_fullname'] == self.recipient.full_name()
        assert delivery['planned_delivery_date'] == self.asof.isoformat()
        assert delivery['package_type'] == self.package_type.id
        assert delivery['package_type_name'] == self.package_type.name

    def test_should_get_filterd_user_deliveries(self):
        delivery = Delivery.objects.create(
            delivery_from=self.adopter.profile,
            delivery_to=self.recipient,
            package_type=self.package_type,
            planned_delivery_date=self.asof,
            package_description='',
            delivery_description='',
        )

        response = self.get_deliveries(status=Delivery.STATUS_PLANNED)
        assert len(response.data) == 2

        delivery.status = Delivery.STATUS_DELIVERED
        delivery.save()
        response = self.get_deliveries(status=Delivery.STATUS_DELIVERED)
        assert len(response.data) == 1

        delivery.status = Delivery.STATUS_CANCELED
        delivery.save()
        response = self.get_deliveries(status=Delivery.STATUS_CANCELED)
        assert len(response.data) == 1

    def test_should_get_only_users_deliveries(self):
        response = self.get_deliveries(client=self.other_authenticated_client)
        assert len(response.data) == 0

    def test_should_not_get_deliveries_for_anonymous_user(self):
        response = self.get_deliveries(client=self.anonymous_client)
        assert response.status_code == 401

    def test_should_get_deliveries_filtered_by_adopted_recipients(self):
        response = self.get_deliveries(for_adopted_recipients=1)
        assert len(response.data) == 0

        Adoption.objects.create(
            adopter=self.adopter.profile,
            recipient=self.recipient,
            status=Adoption.STATUS_APPROVED,
        )

        response = self.get_deliveries(for_adopted_recipients=1)
        assert len(response.data) == 1

    def test_should_create_delivery(self):
        response = self.create_delivery()
        assert response.status_code == 201

        delivery = Delivery.objects.get(id=response.data['id'])

        assert delivery.delivery_from == self.adopter.profile
        assert delivery.delivery_to == self.recipient
        assert delivery.status == Delivery.STATUS_DELIVERED
        assert delivery.planned_delivery_date == delivery.created_at.date()
        assert delivery.package_type == self.package_type
        assert delivery.package_description == ''
        assert delivery.delivery_description == ''

    def test_should_not_create_delivery_with_status_canceled(self):
        response = self.create_delivery(status=Delivery.STATUS_CANCELED)
        assert response.status_code == 400

    def test_should_update_only_user_deliveries(self):
        response = self.update_delivery(
            delivery_id=self.delivery.id,
            client=self.other_authenticated_client,
        )
        assert response.status_code == 404

    def test_should_update_delivery_as_delivered(self):
        response = self.update_delivery(delivery_id=self.delivery.id)
        assert response.status_code == 200

        self.delivery.refresh_from_db()
        assert self.delivery.status == Delivery.STATUS_DELIVERED

    def test_should_update_delivery_as_pending(self):
        response = self.update_delivery(
            delivery_id=self.delivery.id,
            status=Delivery.STATUS_PENDING,
        )
        assert response.status_code == 200

        self.delivery.refresh_from_db()
        assert self.delivery.status == Delivery.STATUS_PENDING

    def test_should_not_update_non_existing_delivery(self):
        response = self.update_delivery(delivery_id=-1)
        assert response.status_code == 404

    def test_should_not_update_delivery_with_terminal_status(self):
        for status in [
            Delivery.STATUS_DELIVERED,
            Delivery.STATUS_CANCELED,
        ]:
            with self.subTest(status):
                self.delivery.status = status
                self.delivery.save()

                response = self.update_delivery(
                    delivery_id=self.delivery.id,
                    status=Delivery.STATUS_PENDING,
                )

                assert response.status_code == 400
