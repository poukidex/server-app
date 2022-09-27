from __future__ import annotations

import binascii
import os
import uuid
from datetime import datetime

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(
        self, username: str, password: str, **extra_fields
    ) -> AbstractUser:
        if not username:
            raise ValueError("The given username must be set")

        user: AbstractUser = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username: str, password: str, **extra_fields) -> AbstractUser:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

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

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects: UserManager = UserManager()

    def __str__(self):
        return f"{self.username}"

