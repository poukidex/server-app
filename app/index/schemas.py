from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db import models
from ninja import Field, Schema
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


class PropositionUpdate(Schema):
    comment: str


class PropositionInput(PropositionUpdate):
    object_name: str
    dominant_colors: Optional[dict]


class PropositionSchema(PropositionInput):
    id: UUID
    created_at: datetime
    user_id: UUID
    user_username: str = Field(alias="user.username")
    presigned_url: str
    nb_likes: Optional[int] = 0
    nb_dislikes: Optional[int] = 0


class ExtendedPropositionSchema(PropositionSchema):
    pass


class PublicationUpdate(Schema):
    name: str
    description: str


class PublicationInput(PublicationUpdate):
    object_name: str
    dominant_colors: Optional[dict]


class PublicationSchema(PublicationInput):
    id: UUID
    created_at: datetime
    presigned_url: str


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
    nb_items: Optional[int]


class ExtendedIndexSchema(IndexSchema):
    publications: list[PublicationSchema]
