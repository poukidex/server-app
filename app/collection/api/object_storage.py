import uuid
from http import HTTPStatus

from ninja import Router

from config.external_client import s3_client
from core.schemas.common import ImageUploadInput, ImageUploadSchema

router = Router()


@router.post(
    path="/presigned-url",
    url_name="generate_presigned_url",
    response={HTTPStatus.OK: ImageUploadSchema},
    operation_id="generate_upload_presigned_url",
)
def generate_upload_presigned_url(request, payload: ImageUploadInput):
    object_name = f"{payload.id}/{uuid.uuid4()}-{payload.filename}"

    presigned_url = s3_client.generate_presigned_post_url(
        object_name, payload.content_type
    )

    return ImageUploadSchema(object_name=object_name, presigned_url=presigned_url)
