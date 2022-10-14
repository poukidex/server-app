import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField
from userauth.utils import upload_to

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

    picture = ResizedImageField(
        size=[200, 200],
        crop=["middle", "center"],
        upload_to=upload_to,
        default="user.png",
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects: UserManager = UserManager()

    def __str__(self):
        return f"{self.username}"
