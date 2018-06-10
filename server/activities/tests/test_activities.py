import datetime
from unittest import mock
from urllib.parse import urlencode

from django.urls import reverse

from common.tests import temporarily
from recipients.models import Recipient
from adoptions.models import PackageType, Delivery
from .base import ActivityDayBase
from ..models import ActivityDayVolunteer, ActivityDayDelivery

DEFAULT = object()


def default(value, default):
    return value if value is not DEFAULT else default


class TestActivityDay(ActivityDayBase):

    @classmethod
    def get_activites(
        cls,
        asof,
        from_date=DEFAULT,
        to_date=DEFAULT,
        activity_type=DEFAULT,
        logistics_center=DEFAULT,
    ):
        from_date = default(from_date, None)
        to_date = default(to_date, None)
        activity_type = default(activity_type, None)
        logistics_center = default(logistics_center, None)
        params = {
            'from_date': from_date,
            'to_date': to_date,
            'activity_type': activity_type,
            'logistics_center': logistics_center,
        }
        params = urlencode({k: v for k, v in params.items() if v is not None})

        with mock.patch('activities.views.now') as mocked:
            mocked.return_value = asof

            return cls.anonymous_client.get('{}?{}'.format(
                    reverse('activityday-list'),
                    params,
            ))

    def test_should_get_activity_types(self):
        response = self.anonymous_client.get(reverse('activitytype-list'))

        assert len(response.data) == 1
        assert response.data[0]['id'] == self.activity_type.id
        assert response.data[0]['description'] == self.activity_type.description

    def test_should_get_future_activities(self):
        response = self.get_activites(
            asof=self.activity.date - datetime.timedelta(days=1),
        )

        assert len(response.data) == 2

        activity = response.data[0]
        assert activity['id'] == self.activity.id
        assert activity['date'] == self.activity.date.isoformat()
        assert activity['type']['id'] == self.activity.type_id
        assert activity['logistics_center']['description'] == self.activity.logistics_center.description
        assert activity['logistics_center']['address'] == (
            self.activity.logistics_center.address()
        )

        response = self.get_activites(
            asof=self.activity2.date + datetime.timedelta(days=1),
        )
        assert len(response.data) == 0

    def test_should_get_only_website_display_activities(self):
        response = self.get_activites(
            asof=self.activity.date - datetime.timedelta(days=1),
        )

        assert len(response.data) == 2

        with temporarily(self.activity2, display_in_website=False):
            response = self.get_activites(
                asof=self.activity.date - datetime.timedelta(days=1),
            )

            assert len(response.data) == 1

    def test_should_get_filtered_activites(self):
        response = self.get_activites(
            asof=self.activity.date - datetime.timedelta(days=1),
            from_date=self.activity.date - datetime.timedelta(days=2),
            to_date=self.activity.date + datetime.timedelta(days=2),
            activity_type=self.activity.type_id,
            logistics_center=self.activity.logistics_center_id,
        )
        assert len(response.data) == 2

        response = self.get_activites(
            asof=self.activity.date - datetime.timedelta(days=1),
            from_date=self.activity.date - datetime.timedelta(days=2),
            to_date=self.activity.date + datetime.timedelta(days=2),
            activity_type=-1,
            logistics_center=-1,
        )
        assert len(response.data) == 0


class TestActivityDayVolunteer(ActivityDayBase):

    @classmethod
    def register_for_activity_day(
        cls,
        activity_day_id,
        client=DEFAULT,
    ):
        client = default(client, cls.authenticated_client)

        return client.post(reverse('activityday-volunteer-list'), {
            'activity_day': activity_day_id,
        })

    @classmethod
    def get_activities_for_volunteer(
        cls,
        from_date=DEFAULT,
        to_date=DEFAULT,
        client=DEFAULT,
    ):
        client = default(client, cls.authenticated_client)
        from_date = default(from_date, None)
        to_date = default(to_date, None)

        params = {
            'from_date': from_date.isoformat() if from_date is not None else None,
            'to_date': to_date.isoformat() if to_date is not None else None,
        }

        params = urlencode({k: v for k, v in params.items() if v is not None})

        return client.get('{}?{}'.format(
            reverse('activityday-volunteer-list'),
            params,
        ))

    def test_should_volunteer_for_activity_day(self):
        assert not ActivityDayVolunteer.objects.filter(
            volunteer=self.volunteer.profile,
            activity_day=self.activity,
        ).exists()

        response = self.register_for_activity_day(
            activity_day_id=self.activity.id,
        )

        assert response.status_code == 201

        assert ActivityDayVolunteer.objects.filter(
            volunteer=self.volunteer.profile,
            activity_day=self.activity,
        ).exists()

    def test_should_handle_idempotency_activity_day_request(self):
        response = self.register_for_activity_day(
            activity_day_id=self.activity.id,
        )
        assert response.status_code == 201
        assert ActivityDayVolunteer.objects.filter(
            volunteer=self.volunteer.profile,
            activity_day=self.activity,
        ).count() == 1

        response = self.register_for_activity_day(
            activity_day_id=self.activity.id,
        )
        assert ActivityDayVolunteer.objects.filter(
            activity_day=self.activity,
            volunteer=self.volunteer.profile,
        ).count() == 1

    def test_should_not_volunteer_for_activity_day_for_anonymous_user(self):
        response = self.register_for_activity_day(
            activity_day_id=self.activity.id,
            client=self.anonymous_client,
        )
        assert response.status_code == 401

    def test_should_get_volunteer_day_activities(self):
        self.register_for_activity_day(
            activity_day_id=self.activity.id,
        )
        response = self.get_activities_for_volunteer()
        assert len(response.data) == 1

        activity_day = response.data[0]

        assert activity_day['activity_day'] == self.activity.id
        assert activity_day['date'] == self.activity.date.isoformat()
        assert activity_day['logistics_center']['description'] == (
            self.activity.logistics_center.description
        )
        assert activity_day['activity_type']['description'] == self.activity.type.description

    def test_should_not_get_other_users_activities(self):
        self.register_for_activity_day(
            activity_day_id=self.activity.id,
            client=self.other_authenticated_client,
        )
        response = self.get_activities_for_volunteer(
            client=self.authenticated_client,
        )
        assert len(response.data) == 0

    def test_should_get_filtered_activites(self):
        self.register_for_activity_day(
            activity_day_id=self.activity.id,
        )

        response = self.get_activities_for_volunteer(
            from_date=self.activity.date + datetime.timedelta(days=1),
        )
        assert len(response.data) == 0

        response = self.get_activities_for_volunteer(
            to_date=self.activity.date - datetime.timedelta(days=1),
        )
        assert len(response.data) == 0

        response = self.get_activities_for_volunteer(
            to_date=self.activity.date + datetime.timedelta(days=1),
            from_date=self.activity.date - datetime.timedelta(days=1),
        )
        assert len(response.data) == 1


class TestActivityDayDelivery(ActivityDayBase):
    @classmethod
    def get_activites_deliveries(
        cls,
        client=DEFAULT,
        recipient_uid=DEFAULT,
        delivery_id=DEFAULT,
        package_type=DEFAULT,
        description=DEFAULT,
        status=DEFAULT,
        status_date=DEFAULT,
    ):
        client = default(client, cls.authenticated_client)
        recipient_uid = default(recipient_uid, None)
        delivery_id = default(delivery_id, None)
        package_type = default(package_type, None)
        description = default(description, None)
        status = default(status, None)
        status_date = default(status_date, None)

        params = {
            'recipient_uid': recipient_uid,
            'delivery_id': delivery_id,
            'package_type': package_type,
            'description': description,
            'status': status,
            'status_date': status_date,
        }
        params = urlencode({k: v for k, v in params.items() if v is not None})

        return client.get('{}?{}'.format(
            reverse('activityday-delivery-list'),
            params,
        ))

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.recipient = Recipient.objects.create(
            first_name='foo',
            last_name='bar',
            phone='999999999',
            street=cls.street,
            street_number=2,
            floor=2,
            apartment=2,
            recipient_tags=[Recipient.RECIPIENT_TAG_SINGLE_PARENT],
            background_story='this is my background.',
            number_of_people=2,
        )
        cls.asof = datetime.date(1947, 1, 1)

        cls.package_type = PackageType.objects.create(
            name='package',
            description='description',
        )
        cls.delivery = Delivery.objects.create(
            delivery_from=cls.volunteer.profile,
            delivery_to=cls.recipient,
            package_type=cls.package_type,
            planned_delivery_date=cls.asof,
            package_description='',
            delivery_description='this is the delivery description',
        )

    def test_should_get_user_delivery_activities(self):
        # ActivityDayDelivery created by admin.
        ActivityDayDelivery.objects.create(
            activity_day=self.activity,
            delivery=self.delivery,
        )
        response = self.get_activites_deliveries()

        assert len(response.data) == 1

        delivery = response.data[0]
        assert delivery['activity_day'] == self.activity.pk
        assert delivery['delivery']['id'] == self.delivery.id
        assert delivery['delivery']['delivery_to'] == str(self.recipient.uid)
        assert delivery['delivery']['delivery_to_phone'] == self.recipient.phone
        assert delivery['delivery']['delivery_to_address'] == self.recipient.address()
        assert delivery['delivery']['package_type'] == self.delivery.package_type.id
        assert delivery['delivery']['status'] == self.delivery.status
        assert delivery['delivery']['status_set_at'] == self.delivery.status_set_at.strftime('%d/%m/%y')

    def test_should_get_user_delivery_activities_filtered_by_recipient(self):
        ActivityDayDelivery.objects.create(
            activity_day=self.activity,
            delivery=self.delivery,
        )
        response = self.get_activites_deliveries(
            recipient_uid=self.recipient.uid,
        )
        len(response.data) == 1
        response = self.get_activites_deliveries(
            recipient_uid='uid',
        )

        assert len(response.data) == 0

    def test_should_get_user_delivery_activities_filtered_by_package_type(self):
        ActivityDayDelivery.objects.create(
            activity_day=self.activity,
            delivery=self.delivery,
        )
        response = self.get_activites_deliveries(
            package_type=self.delivery.package_type_id,
        )
        assert len(response.data) == 1

        response = self.get_activites_deliveries(
            package_type=-1,
        )
        assert len(response.data) == 0

    def test_should_get_user_delivery_activities_filtered_by_description(self):
        ActivityDayDelivery.objects.create(
            activity_day=self.activity,
            delivery=self.delivery,
        )
        response = self.get_activites_deliveries(
            description='bla bla',
        )
        assert len(response.data) == 0

    def test_should_get_user_delivery_activities_filtered_by_status(self):
        ActivityDayDelivery.objects.create(
            activity_day=self.activity,
            delivery=self.delivery,
        )
        response = self.get_activites_deliveries(
            status=Delivery.STATUS_DELIVERED,
        )

        assert len(response.data) == 0

    def test_should_get_only_deliveries_with_associated_activity_day(self):
        response = self.get_activites_deliveries()

        assert len(response.data) == 0
