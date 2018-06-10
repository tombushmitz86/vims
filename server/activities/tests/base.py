import datetime

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from geography.models import Settlement, Street
from logistics.models import LogisticsCenter
from users.models import UserProfile
from ..models import ActivityDay, ActivityType


class ActivityDayBase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.anonymous_client = APIClient()

        settlement = Settlement.objects.create(
            gov_id=1,
            name='settlement',
            county_gov_id=2,
            county_name='county name',
            municipality_gov_id=3,
            municipality_name='munic',
        )
        cls.street = Street.objects.create(
            settlement=settlement,
            gov_id=2,
            name='street',
        )
        cls.logistic_center = LogisticsCenter.objects.create(
            description='logistic center',
            street=cls.street,
            street_number=1,
            contact_person='Bob',
            phone='9729999999999',
        )
        cls.activity_type = ActivityType.objects.create(
            description='activity type',
        )
        cls.activity = ActivityDay.objects.create(
            type=cls.activity_type,
            date=datetime.date(2018, 1, 1),
            logistics_center=cls.logistic_center,
        )
        cls.activity2 = ActivityDay.objects.create(
            type=cls.activity_type,
            date=datetime.date(2018, 1, 2),
            logistics_center=cls.logistic_center,
        )

        cls.authenticated_client = APIClient()
        cls.other_authenticated_client = APIClient()

        cls.volunteer = get_user_model().objects.create(
            email='volunteer@email.com',
            password='pass'
        )
        cls.other_volunteer = get_user_model().objects.create(
            email='other_volunteer@email.com',
            password='pass'
        )

        cls.authenticated_client.force_authenticate(user=cls.volunteer)
        cls.other_authenticated_client.force_authenticate(
            user=cls.other_volunteer,
        )

        UserProfile.objects.create(
            user=cls.volunteer,
            phone='999999999',
            street=cls.street,
            street_number=2,
            floor=2,
            apartment=2,
            zipcode='99999',
        )
        UserProfile.objects.create(
            user=cls.other_volunteer,
            phone='999999999',
            street=cls.street,
            street_number=2,
            floor=2,
            apartment=2,
            zipcode='99999',
        )
