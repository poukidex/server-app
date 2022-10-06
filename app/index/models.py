import uuid
from datetime import datetime

from django.db import models
from userauth.models import User

from index.schemas import ValidationMode


class Index(models.Model):
    id: uuid.UUID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)

    name: str = models.CharField(
        max_length=16, choices=ValidationMode.choices, default=ValidationMode.USER
    )

    created_by: User = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="indexes"
    )

    validation_mode: ValidationMode = models.CharField(
        max_length=16, choices=ValidationMode.choices, default=ValidationMode.USER
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_index_name",
            ),
        ]


class Publication(models.Model):
    id: uuid.UUID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)

    index: Index = models.ForeignKey(
        Index, on_delete=models.CASCADE, related_name="publications"
    )

    object_name: str = models.CharField(max_length=255)


class Proposition(models.Model):
    id: uuid.UUID = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at: datetime = models.DateTimeField(auto_now_add=True)

    publication: Publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="publications"
    )

    user: User = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="publications"
    )

    object_name: str = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "user"],
                name="unique_proposition_publication_user",
            ),
        ]
