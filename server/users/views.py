from django.contrib.auth import authenticate
from django.contrib.auth.signals import user_logged_in
from djoser import views as djoser_views
from rest_framework import views
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, AuthenticationFailed

from . import serializers
from . import models

class UserRegisterationView(djoser_views.UserCreateView):
    serializer_class = serializers.UserRegistrationSerializer


class UserLoginView(views.APIView):

    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']
        except (KeyError, TypeError):
            raise ParseError()
        if not isinstance(email, str) or not isinstance(password, str):
            raise ParseError()

        user = authenticate(
            request=request,
            email=email,
            password=password,
        )

        if user is None:
            raise AuthenticationFailed('Invalid credentials')

        try:
            user.profile
        except models.UserProfile.DoesNotExist:
            raise AuthenticationFailed('User has no profile')

        token, _ = Token.objects.get_or_create(user=user)

        user_logged_in.send(
            sender=user.__class__,
            request=request,
            user=user,
        )

        return Response({
            'token': token.key,
        })


class UserProfileView(views.APIView):
    serializer_class = serializers.UserDetailsSerializer

    def put(self, request):
        serializer = self.serializer_class(request.user.profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def get(self, request):
        serializer = self.serializer_class(request.user.profile)
        return Response(serializer.data)
