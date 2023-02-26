import uuid

from config.external_client import s3_client

from index.schemas import ImageUploadSchema


def generate_presigned_url_for_object(object, filename, content_type):
    object_name = f"{object.id}/{uuid.uuid4()}-{filename}"

    presigned_url = s3_client.generate_presigned_post_url(object_name, content_type)

    return ImageUploadSchema(object_name=object_name, presigned_url=presigned_url)
