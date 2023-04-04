from django.db import models


class ValidationMode(models.TextChoices):
    Manual = "Manual"
    Everything = "Everything"


class PendingPublicationStatus(models.TextChoices):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFUSED = "refused"
