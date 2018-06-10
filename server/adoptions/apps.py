from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AdoptionsConfig(AppConfig):
    name = 'adoptions'
    verbose_name = _('Adoptions and deliveries')
