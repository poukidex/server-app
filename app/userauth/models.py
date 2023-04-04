from __future__ import annotations

import binascii
import os

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import Identifiable, Storable, Traceable
from core.utils import check_object


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(
        self, username: str, password: str, **extra_fields
    ) -> AbstractUser:
        if not username:
            raise ValueError("The given username must be set")

        user: AbstractUser = self.model(username=username, **extra_fields)
        user.set_password(password)

        check_object(user)

        user.save(using=self._db)
        return user

    def create_user(self, username: str, password: str, **extra_fields) -> AbstractUser:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, password, **extra_fields)


class User(AbstractUser, Identifiable, Storable, Traceable):
    email = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()
    auth_token: Token

    def __str__(self):
        return f"{self.username}"

    def fullname(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return f"{self.username}"


class Token(models.Model):
    """
    The default authorization token model.
    """

    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        User,
        related_name="auth_token",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs) -> None:
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
