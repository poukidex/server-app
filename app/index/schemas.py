from datetime import datetime
from typing import Optional
from uuid import UUID

from ninja import Schema

from core.enums import ValidationMode
from userauth.schemas import UserSchema


# ======================================================================================
# Approbation
# ======================================================================================
class ApprobationQuery(Schema):
    approved: Optional[bool]


class ApprobationInput(Schema):
    approved: bool


class ApprobationSchema(Schema):
    id: int
    user: UserSchema
    approved: bool


# ======================================================================================
# Proposition
# ======================================================================================
class PropositionInput(Schema):
    object_name: str
    comment: str
    dominant_colors: Optional[dict]


class PropositionUpdate(Schema):
    object_name: str
    comment: str
    dominant_colors: Optional[dict]


class PropositionSchema(Schema):
    id: UUID
    created_at: datetime
    user: UserSchema
    comment: str
    dominant_colors: Optional[dict]

    presigned_url: str
    nb_likes: Optional[int] = 0
    nb_dislikes: Optional[int] = 0


# ======================================================================================
# Publication
# ======================================================================================
class PublicationInput(Schema):
    name: str
    description: str
    object_name: str
    dominant_colors: Optional[dict]


class PublicationUpdate(Schema):
    name: str
    description: str
    object_name: str
    dominant_colors: Optional[dict]


class PublicationSchema(Schema):
    id: UUID
    name: str
    description: str
    created_at: datetime
    dominant_colors: Optional[dict]

    presigned_url: str
    nb_captures: Optional[int] = 0


# ======================================================================================
# Index
# ======================================================================================
class IndexInput(Schema):
    name: str
    description: str
    object_name: Optional[str]


class IndexUpdate(Schema):
    name: str
    description: str
    object_name: Optional[str]


class IndexSchema(Schema):
    id: UUID
    name: str
    description: str
    created_at: datetime
    creator: UserSchema
    validation_mode: ValidationMode

    presigned_url: Optional[str]
    nb_items: Optional[int] = 0
