from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db import models
from ninja import Field, Schema
from userauth.schemas import UserSchema


class ApprobationInput(Schema):
    approved: bool


class ApprobationQuery(Schema):
    approved: Optional[bool]


class ApprobationSchema(Schema):
    id: int
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
    dominant_colors: Optional[dict]


class PropositionUpdate(PropositionInput):
    pass


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


class PublicationInput(Schema):
    object_name: str
    name: str
    description: str
    dominant_colors: Optional[dict]


class PublicationUpdate(PublicationInput):
    pass


class PublicationSchema(PublicationInput):
    id: UUID
    created_at: datetime
    presigned_url: str
    nb_captures: Optional[int] = 0


class ExtendedPublicationSchema(PublicationSchema):
    pass


class ValidationMode(models.TextChoices):
    Manual = "Manual"
    Everything = "Everything"


class IndexInput(Schema):
    name: str
    description: str


class IndexUpdate(IndexInput):
    pass


class IndexSchema(Schema):
    id: UUID
    name: str
    description: str
    created_at: datetime
    creator_id: UUID
    creator_username: str = Field(alias="creator.username")
    validation_mode: ValidationMode
    nb_items: Optional[int] = 0


class ExtendedIndexSchema(IndexSchema):
    pass
