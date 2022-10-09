import uuid

from config.external_client import s3_client
from django.db import models
from userauth.models import User

from index.schemas import ValidationMode


class Index(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255)

    creator = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="indexes"
    )

    validation_mode = models.CharField(
        max_length=16, choices=ValidationMode.choices, default=ValidationMode.Manual
    )

    def __str__(self):
        return f"Index {self.name} created by {self.creator}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_index_name",
            ),
        ]


class Publication(models.Model):
    index = models.ForeignKey(
        Index, on_delete=models.CASCADE, related_name="publications"
    )

    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    name = models.CharField(max_length=63)
    description = models.CharField(max_length=255)
    object_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Publication {self.name} of {self.index}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "index"],
                name="unique_publication_index_name",
            ),
        ]


class Proposition(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="propositions"
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="propositions"
    )

    comment = models.CharField(max_length=255)

    object_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Proposition of {self.user} on {self.publication}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "user"],
                name="unique_proposition_publication_user",
            ),
        ]

    @property
    def presigned_url(self):
        return s3_client.generate_presigned_url(self.object_name)


class Approbation(models.Model):
    proposition = models.ForeignKey(
        Proposition, on_delete=models.CASCADE, related_name="approbations"
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="approbations"
    )

    approved = models.BooleanField(default=True)

    def __str__(self):
        approbation = "Approbation" if self.approved else "Disapprobation"
        return f"{approbation} by {self.user} on {self.proposition}"
