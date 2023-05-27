from typing import Optional
from uuid import UUID

from ninja import Schema


class ErrorOutput(Schema):
    status: int
    message: str
    detail: dict[str, str]


class ImageUploadInput(Schema):
    id: UUID
    filename: str
    content_type: str


class PresignedUrlFile(Schema):
    url: str
    fields: dict[str, str]


class ImageUploadSchema(Schema):
    object_name: str
    presigned_url: PresignedUrlFile


class IdentifiableOutput(Schema):
    id: UUID


class RepresentableOutput(Schema):
    name: str
    description: str


class BaseStorable(Schema):
    dominant_colors: Optional[dict]


class StorableInput(BaseStorable):
    object_name: str


class OptionalStorableInput(BaseStorable):
    object_name: Optional[str]


class StorableOutput(BaseStorable):
    object_name: str
    presigned_url: str


class OptionalStorableOutput(BaseStorable):
    object_name: Optional[str]
    presigned_url: Optional[str]
