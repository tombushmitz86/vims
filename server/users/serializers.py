from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, password_validation
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from . import models


class UserProfileSerializer(serializers.ModelSerializer):
    settlement = serializers.PrimaryKeyRelatedField(source='street.settlement', read_only=True)

    class Meta:
        model = models.UserProfile
        fields = (
            'phone',
            'street',
            'settlement',
            'street_number',
            'floor',
            'apartment',
            'zipcode',
        )


class UserRegistrationSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(many=False)

    class Meta:
        model = get_user_model()
        fields = (
            'email',
            'first_name',
            'last_name',
            'password',
            'profile',
        )

        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, validated_data):
        if get_user_model().objects.filter(email__iexact=validated_data['email']).exists():
            raise serializers.ValidationError(_('User with same email already exists'))

        try:
            password_validation.validate_password(validated_data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages[0]) from None

        return validated_data

    @db_transaction.atomic
    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False,
        )
        UserProfileSerializer(data=validated_data['profile'])
        models.UserProfile.objects.create(
            user=user,
            **validated_data['profile'],
        )

        return user


class UserDetailsSerializer(UserProfileSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email')
    password = serializers.CharField(source='user.password', write_only=True)

    class Meta:
        model = models.UserProfile
        fields = UserProfileSerializer.Meta.fields + (
            'full_name',
            'email',
            'password'
        )

    def update(self, instance, validated_data):
        user_details = validated_data.pop('user')
        password = user_details.get('password')
        email = user_details.pop('email')

        if password is not None:
            instance.user.set_password(password)

        if email is not None:
            instance.user.email = email

        instance.phone = validated_data.get('phone', instance.phone)
        instance.street = validated_data.get('street', instance.street)
        instance.street_number = validated_data.get('street_number', instance.street_number)
        instance.floor = validated_data.get('floor', instance.floor)
        instance.apartment = validated_data.get('apartment', instance.apartment)
        instance.zipcode = validated_data.get('zipcode', instance.zipcode)

        instance.user.save()
        instance.save()

        return instance
