from django.db import models


class PendingItemStatus(models.TextChoices):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REFUSED = "refused"
