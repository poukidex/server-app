from django.db import models


class ValidationMode(models.TextChoices):
    Manual = "Manual"
    Everything = "Everything"
