from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from users.models import UserProfile
from geography.models import Settlement, Street
from recipients.models import Recipient


class TestAdoptionBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anonymous_client = APIClient()
        cls.authenticated_client = APIClient()
        cls.other_authenticated_client = APIClient()

        cls.adopter = get_user_model().objects.create(
            email='adopter@email.com',
            password='pass'
        )
        cls.other_adopter = get_user_model().objects.create(
            email='other_adopter@email.com',
            password='pass'
        )

        cls.authenticated_client.force_authenticate(user=cls.adopter)
        cls.other_authenticated_client.force_authenticate(user=cls.other_adopter)

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
            user=cls.adopter,
            phone='999999999',
            street=street,
            street_number=2,
            floor=2,
            apartment=2,
            zipcode='99999',
        )
        UserProfile.objects.create(
            user=cls.other_adopter,
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
