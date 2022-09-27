from datetime import datetime
from typing import Optional
from uuid import UUID
from django import models
from ninja import Schema

class ValidationMode(models.TextChoices):
    Manual = "Manual"
    Everything = "Everything"

class BaseErrorResponse(Schema):
    detail: str

class IndexInput(Schema):
    name: str
    validation_mode: Optional[ValidationMode] = ValidationMode.Manual

class IndexSchema(Schema):
    id: UUID
    created_at: datetime
    created_by_id: UUID
    validation_mode: ValidationMode

class PublicationInput(Schema):
    pass

class PublicationSchema(Schema):
    id: UUID
    created_at: datetime
    object_name: str


class PropositionInput(Schema):
    pass

class PropositionSchema(Schema):
    id: UUID
    created_at: datetime
    user_id: UUID
    object_name: str