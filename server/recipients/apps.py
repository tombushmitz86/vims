from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RecipientsConfig(AppConfig):
    name = 'recipients'
    verbose_name = _('Recipients')
