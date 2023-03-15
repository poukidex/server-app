from __future__ import annotations

import binascii
import os
import uuid

from config.external_client import s3_client
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from index.utils import check_object


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


class User(AbstractUser):
    id: uuid.UUID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    email: str = models.EmailField(
        _("email address"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )

    picture_object_name: str = models.CharField(
        null=True, blank=True, max_length=255, verbose_name="Picture object name"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects: UserManager = UserManager()
    auth_token: Token

    def __str__(self):
        return f"{self.username}"

    @property
    def picture_presigned_url(self):
        if not self.picture_object_name:
            return None
        return s3_client.generate_presigned_url(self.picture_object_name)


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
