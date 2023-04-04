from django.db import models

from core.models import Identifiable, Representable, Storable, Traceable
from index.schemas import ValidationMode
from userauth.models import User


class Index(Identifiable, Representable, Traceable, Storable):
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


class Publication(Identifiable, Representable, Traceable, Storable):
    index = models.ForeignKey(
        Index, on_delete=models.CASCADE, related_name="publications"
    )

    def __str__(self):
        return f"Publication {self.name} of {self.index}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "index"],
                name="unique_publication_index_name",
            ),
        ]


class Proposition(Identifiable, Traceable, Storable):
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


class Approbation(Traceable):
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["proposition", "user"],
                name="unique_approbation_user_proposition",
            ),
        ]
