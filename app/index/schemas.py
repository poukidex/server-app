from datetime import datetime
from typing import Optional

from ninja import Schema

from core.enums import ValidationMode
from core.schemas import (
    IdentifiableOutput,
    OptionalStorableInput,
    OptionalStorableOutput,
    RepresentableOutput,
    StorableInput,
    StorableOutput,
)
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
class PropositionInput(StorableInput):
    comment: str


class PropositionUpdate(StorableInput):
    comment: str


class PropositionSchema(IdentifiableOutput, StorableOutput):
    created_at: datetime
    user: UserSchema
    comment: str

    nb_likes: Optional[int] = 0
    nb_dislikes: Optional[int] = 0


# ======================================================================================
# Publication
# ======================================================================================
class PublicationInput(RepresentableOutput, StorableInput):
    pass


class PublicationUpdate(RepresentableOutput, StorableInput):
    pass


class PublicationSchema(IdentifiableOutput, RepresentableOutput, StorableOutput):
    created_at: datetime
    nb_captures: Optional[int] = 0


# ======================================================================================
# Index
# ======================================================================================
class IndexInput(RepresentableOutput, OptionalStorableInput):
    pass


class IndexUpdate(RepresentableOutput, OptionalStorableInput):
    pass


class IndexSchema(IdentifiableOutput, RepresentableOutput, OptionalStorableOutput):
    created_at: datetime
    creator: UserSchema
    validation_mode: ValidationMode

    nb_items: Optional[int] = 0
