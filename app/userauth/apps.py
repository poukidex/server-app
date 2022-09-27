from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthUserConfig(AppConfig):
    name = "userauth"
    verbose_name = _("User Auth")