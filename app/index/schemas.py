from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db import models
from ninja import Schema


class PropositionUploadInput(Schema):
    filename: str


class PropositionUploadSchema(Schema):
    object_name: str
    presigned_url: str


class PropositionInput(Schema):
    object_name: str
    comment: str


class PropositionUpdate(Schema):
    comment: str


class PropositionSchema(Schema):
    id: UUID
    created_at: datetime
    user_id: UUID
    object_name: str
    presigned_url: str
    comment: str


class ExtendedPropositionSchema(PropositionSchema):
    pass


class PublicationUpdate(Schema):
    name: str
    description: str


class PublicationInput(PublicationUpdate):
    pass


class PublicationSchema(PublicationInput):
    id: UUID
    created_at: datetime
    object_name: str


class ExtendedPublicationSchema(PublicationSchema):
    pass


class ValidationMode(models.TextChoices):
    Manual = "Manual"
    Everything = "Everything"


class IndexUpdate(Schema):
    name: str


class IndexInput(Schema):
    name: str
    validation_mode: Optional[ValidationMode] = ValidationMode.Manual


class IndexSchema(Schema):
    id: UUID
    name: str
    created_at: datetime
    created_by_id: UUID
    validation_mode: ValidationMode


class ExtendedIndexSchema(IndexSchema):
    publications: list[PublicationSchema]
