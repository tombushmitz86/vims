import re

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from ..models import User
from geography.models import Settlement, Street


class TestRegistration(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anonymous_client = APIClient()
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

        cls.password = 'sup3rs3cr3t'
        cls.email = 'email@test.testing'
        cls.first_name = 'Foo'
        cls.last_name = 'Bar'
        cls.phone_number = '9999999'
        cls.street_number = 9
        cls.floor = 9
        cls.apartment = 9
        cls.zipcode = '99999'


    def register(self):
        registration_payload = {
            'email': self.email,
            'password': self.password,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'profile': {
                'phone': self.phone_number,
                'street': self.street.pk,
                'street_number': self.street_number,
                'floor': self.floor,
                'apartment': self.apartment,
                'zipcode': self.zipcode,
            }
        }

        return self.anonymous_client.post(reverse('register'), registration_payload)

    def activate(self, uid, token):
        return self.anonymous_client.post(reverse('user-activate'), {
            'uid': uid,
            'token': token,
        })

    def reset_password(self, mail):
        return self.anonymous_client.post(reverse('password-reset'), {
            'email': mail,
        })

    def confirm_reset_password(self, uid, token, new_password):
        return self.anonymous_client.post(reverse('password-reset-confirm'), {
            'uid': uid,
            'token': token,
            'new_password': new_password,
        })

    def test_successful_registration(self):
        before_outbox_len = len(mail.outbox)

        response = self.register()

        user = User.objects.get(email=self.email)
        assert response.status_code == 201
        assert len(mail.outbox) == before_outbox_len + 1
        assert user.first_name == self.first_name
        assert user.last_name == self.last_name
        assert user.check_password(self.password)

        assert user.profile.phone == self.phone_number
        assert user.profile.street == self.street
        assert user.profile.street_number == self.street_number
        assert user.profile.floor == self.floor
        assert user.profile.apartment == self.apartment
        assert user.profile.zipcode == self.zipcode
        assert not user.is_active

        mail_message = mail.outbox[-1]
        mail_body = mail_message.body
        activation_uid, activation_token = re.findall(r'^.*/([^/]+)/([^/]+?)$', mail_body, re.MULTILINE)[0]

        self.activate(activation_uid, activation_token)
        user.refresh_from_db()
        assert user.is_active

        before_outbox_len = len(mail.outbox)
        new_password = 'n3wsup3rs3cr3t'
        self.reset_password(self.email)

        assert len(mail.outbox) == before_outbox_len + 1
        reset_uid, reset_token = re.findall(r'^.*/([^/]+)/([^/]+?)$', mail_body, re.MULTILINE)[0]
        response = self.confirm_reset_password(reset_uid, reset_token, new_password)


        user.refresh_from_db()
        assert response.status_code == 204
        assert not user.check_password(self.password)
        assert user.check_password(new_password)
