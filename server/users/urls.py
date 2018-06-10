from django.conf.urls import url
from djoser import views as djoser_views

from . import views


urlpatterns = [
    url(r'^login/$', views.UserLoginView.as_view(), name='login'),
    url(r'^register/$', views.UserRegisterationView.as_view(), name='register'),
    url(r'^activate/$', djoser_views.ActivationView.as_view(), name='user-activate'),
    url(r'^password/$', djoser_views.SetPasswordView.as_view(), name='set-password'),
    url(r'^password/reset/$', djoser_views.PasswordResetView.as_view(), name='password-reset'),
    url(r'^password/reset/confirm/$', djoser_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    url(r'^userprofile/$', views.UserProfileView.as_view(), name='userprofile'),
]
