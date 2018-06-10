from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from geography.models import Street


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email, password, is_staff=True, is_superuser=True, **extra_fields)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=30,
        blank=True,
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=30,
        blank=True,
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return (self.first_name + ' ' + self.last_name).strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.get_full_name()


class UserProfile(models.Model):
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    user = models.OneToOneField(
        verbose_name=_('User'),
        to=User,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    created_at = models.DateTimeField(
        verbose_name=_('Created at'),
        auto_now_add=True,
        blank=True,
    )
    modified_at = models.DateTimeField(
        verbose_name=_('Modified at'),
        auto_now=True,
        blank=True,
    )
    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=25,
        validators=[
            RegexValidator(r'^[0-9() -]{6,25}$'),
        ],
    )
    street = models.ForeignKey(
        verbose_name=_('Street'),
        to=Street,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='user_profiles',
    )
    street_number = models.IntegerField(
        verbose_name=_('Street number'),
        null=True,
        blank=True,
    )
    floor = models.SmallIntegerField(
        verbose_name=_('Floor'),
        null=True,
        blank=True,
    )
    apartment = models.IntegerField(
        verbose_name=_('Apartment'),
        null=True,
        blank=True,
    )
    zipcode = models.CharField(
        verbose_name=_('Zipcode'),
        max_length=7,
        validators=[
            RegexValidator(r'^\d{5}$|^\d{7}$'),
        ],
        null=True,
        blank=True,
    )

    def address(self):
        return _('{settlement_name}, {street_number} {street_name}, apt. {apartment}, floor {floor}').format(
            settlement_name=self.street.settlement.name,
            street_number=self.street_number,
            street_name=self.street.name,
            apartment=self.apartment,
            floor=self.floor,
        )
    address.short_description = _('Address')

    def __str__(self):
        return str(self.user)
