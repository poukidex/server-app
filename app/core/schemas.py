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
