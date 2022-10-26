from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db import models
from ninja import Schema
from userauth.schemas import UserSchema


class ApprobationInput(Schema):
    approved: bool


class ApprobationSchema(Schema):
    user: UserSchema
    approved: bool


class ImageUploadInput(Schema):
    filename: str
    content_type: str


class PresignedUrlFile(Schema):
    url: str
    fields: dict[str, str]


class ImageUploadSchema(Schema):
    object_name: str
    presigned_url: PresignedUrlFile


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
    approbations: list[ApprobationSchema]


class PublicationUpdate(Schema):
    name: str
    description: str


class PublicationInput(PublicationUpdate):
    object_name: str
    primary_color: Optional[str]
    secondary_color: Optional[str]


class PublicationSchema(PublicationInput):
    id: UUID
    created_at: datetime
    object_name: str
    presigned_url: str
    primary_color: Optional[str]
    secondary_color: Optional[str]


class ExtendedPublicationSchema(PublicationSchema):
    pass


class ValidationMode(models.TextChoices):
    Manual = "Manual"
    Everything = "Everything"


class IndexUpdate(Schema):
    name: str
    description: str


class IndexInput(IndexUpdate):
    validation_mode: Optional[ValidationMode] = ValidationMode.Manual


class IndexSchema(Schema):
    id: UUID
    name: str
    description: str
    created_at: datetime
    creator_id: UUID
    validation_mode: ValidationMode


class ExtendedIndexSchema(IndexSchema):
    publications: list[PublicationSchema]
