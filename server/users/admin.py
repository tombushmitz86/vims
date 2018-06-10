from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ExportMixin

from . import models


class UserProfileResource(resources.ModelResource):
    class Meta:
        model = models.UserProfile
        fields = (
            'user__email',
            'user__first_name',
            'user__last_name',
            'created_at',
            'modified_at',
            'phone',
            'street',
            'street_number',
            'floor',
            'apartment',
            'zipcode',
        )


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    ordering = (
        '-id',
    )
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
    )
    search_fields = (
        'email',
        'first_name',
        'last_name',
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


@admin.register(models.UserProfile)
class UserProfileAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = UserProfileResource

    ordering = (
        '-pk',
    )
    list_display = (
        'pk',
        'full_name',
    )
    search_fields = (
        'user__email',
        'user__first_name',
        'user__last_name',
    )
    list_select_related = (
        'user',
    )

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = (
            'created_at',
            'modified_at',
        )
        if obj:
            readonly_fields += ('user',)
        return readonly_fields

    fields = (
        'user',
        'created_at',
        'modified_at',
        'phone',
        'street',
        'street_number',
        'floor',
        'apartment',
        'zipcode',
    )
    autocomplete_fields = (
        'street',
    )

    def full_name(self, obj):
        return obj.user.get_full_name()
