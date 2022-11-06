from config.external_client import s3_client

from index.schemas import ImageUploadSchema


def generate_presigned_url_for_object(object, filename, content_type):
    object_name = s3_client.generate_object_name(str(object.id), filename)

    presigned_url = s3_client.generate_presigned_upload(object_name, content_type)

    return ImageUploadSchema(object_name=object_name, presigned_url=presigned_url)
