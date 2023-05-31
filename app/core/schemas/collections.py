from datetime import datetime
from typing import Optional

from ninja import Schema

from core.schemas.common import (
    IdentifiableOutput,
    OptionalStorableInput,
    OptionalStorableOutput,
    RepresentableOutput,
    StorableInput,
    StorableOutput,
)
from userauth.schemas import UserSchema


# ======================================================================================
# Like
# ======================================================================================
class LikeQuery(Schema):
    liked: Optional[bool]


class LikeInput(Schema):
    liked: bool


class LikeSchema(Schema):
    id: int
    user: UserSchema
    liked: bool


# ======================================================================================
# Snap
# ======================================================================================
class SnapInput(StorableInput):
    comment: str


class SnapUpdate(StorableInput):
    comment: str


class SnapOutput(IdentifiableOutput, StorableOutput):
    created_at: datetime
    user: UserSchema
    comment: str

    nb_likes: Optional[int] = 0
    nb_dislikes: Optional[int] = 0


# ======================================================================================
# Item
# ======================================================================================
class PendingItemSchema(IdentifiableOutput, RepresentableOutput, StorableOutput):
    created_at: datetime
    creator: UserSchema


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
    creator: UserSchema

    nb_items: Optional[int] = 0
