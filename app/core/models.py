import uuid

from django.db import models

from config.external_client import s3_client


class Identifiable(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    class Meta:
        abstract = True


class Traceable(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Representable(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    class Meta:
        abstract = True


class Storable(models.Model):
    object_name = models.CharField(
        null=True,
        blank=True,
        max_length=255,
    )
    dominant_colors = models.JSONField(null=True, blank=True)

    @property
    def presigned_url(self):
        if not self.object_name:
            return None
        return s3_client.generate_presigned_url(self.object_name)

    class Meta:
        abstract = True
