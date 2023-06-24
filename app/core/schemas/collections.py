from datetime import datetime
from typing import Optional
from uuid import UUID

from ninja import FilterSchema, Schema

from core.schemas.common import (
    IdentifiableOutput,
    OptionalStorableInput,
    OptionalStorableOutput,
    RepresentableOutput,
    StorableInput,
    StorableOutput,
)
from userauth.schemas import UserOutput


# ======================================================================================
# Like
# ======================================================================================
class LikeQuery(FilterSchema):
    liked: Optional[bool]


class LikeInput(Schema):
    liked: bool


class LikeOutput(Schema):
    id: int
    user: UserOutput
    liked: bool


# ======================================================================================
# Snap
# ======================================================================================
class SnapInput(StorableInput):
    comment: str


class SnapOutput(IdentifiableOutput, StorableOutput):
    item_id: UUID
    created_at: datetime
    user: UserOutput
    comment: str

    nb_likes: Optional[int] = 0
    nb_dislikes: Optional[int] = 0


# ======================================================================================
# Item
# ======================================================================================
class PendingItemSchema(IdentifiableOutput, RepresentableOutput, StorableOutput):
    created_at: datetime
    creator: UserOutput


class ItemInput(RepresentableOutput, StorableInput):
    pass


class ItemUpdate(RepresentableOutput, StorableInput):
    pass


class ItemOutput(IdentifiableOutput, RepresentableOutput, StorableOutput):
    created_at: datetime
    dominant_colors: Optional[dict]

    presigned_url: str
    nb_snaps: Optional[int] = 0


# ======================================================================================
# Collection
# ======================================================================================
class CollectionInput(RepresentableOutput, OptionalStorableInput):
    pass


class CollectionOutput(IdentifiableOutput, RepresentableOutput, OptionalStorableOutput):
    created_at: datetime
    creator: UserOutput

    nb_items: Optional[int] = 0
