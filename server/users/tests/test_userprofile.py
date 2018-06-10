from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from geography.models import Street, Settlement
from ..models import User, UserProfile


class TestUserProfile(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.settelment = Settlement.objects.create(
            gov_id=1,
            name='settlement',
            county_gov_id=2,
            county_name='county name',
            municipality_gov_id=1,
            municipality_name='muncipality name',
        )
        cls.street = Street.objects.create(
            settlement=cls.settelment,
            gov_id=1,
            name='street name',
        )
        cls.user = User.objects.create(
            email='foo@bar.com',
            first_name='foo',
            last_name='bar',
        )
        UserProfile.objects.create(
            user=cls.user,
            phone='9999999',
            street=cls.street,
            street_number=9,
            floor=9,
            apartment=9,
            zipcode='99999',
        )
        cls.authenticated_client = APIClient()
        cls.anonymous_client = APIClient()
        cls.authenticated_client.force_authenticate(user=cls.user)

    def test_should_get_profile(self):
        response = self.authenticated_client.get(reverse('userprofile'))

        assert response.data['email'] == self.user.email
        assert response.data['full_name'] == self.user.get_full_name()
        assert response.data['phone'] == self.user.profile.phone
        assert response.data['street'] == self.user.profile.street.id
        assert response.data['street'] == self.user.profile.street.id
        assert response.data['settlement'] == self.user.profile.street.settlement_id
        assert response.data['floor'] == self.user.profile.floor
        assert response.data['apartment'] == self.user.profile.apartment
        assert response.data['zipcode'] == self.user.profile.zipcode

    def test_should_not_get_profile_for_anonymous_user(self):
        response = self.anonymous_client.get(reverse('userprofile'))
        assert response.status_code == 401

    def test_should_update_profile(self):
        new_details = {
            'email': 'newmail@bar.com',
            'password': 'sup3rs3cr3t2',
            'phone': '9999999',
            'street_number': 9,
            'street': self.street.id,
            'floor': 9,
            'apartment': 9,
            'zipcode': '99999',
        }
        response = self.authenticated_client.put(reverse('userprofile'), new_details)

        assert response.status_code == 200

        self.user.refresh_from_db()

        assert self.user.check_password(new_details['password'])
        assert self.user.email == new_details['email']

        assert self.user.profile.phone == new_details['phone']
        assert self.user.profile.street_number == new_details['street_number']
        assert self.user.profile.street_id == new_details['street']
        assert self.user.profile.floor == new_details['floor']
        assert self.user.profile.apartment == new_details['apartment']
        assert self.user.profile.zipcode == new_details['zipcode']
