import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Optional

from django.db.models import Count, Q
from generators.pagination import OverpoweredPagination
from ninja import Router
from ninja.pagination import paginate

from config.external_client import s3_client
from core.models.collections import Snap
from core.schemas.collections import SnapOutput
from core.schemas.common import ImageUploadInput, ImageUploadSchema

router = Router()


@router.get(
    path="/feed",
    url_name="feed",
    response={HTTPStatus.OK: list[SnapOutput]},
    operation_id="get_feed",
)
@paginate(OverpoweredPagination)
def retrieve_feed(_request, since: Optional[datetime] = None):
    snaps = Snap.objects.select_related("item__collection").annotate(
        nb_likes=Count("likes", filter=Q(likes__liked=True)),
    )

    if since:
        snaps = snaps.filter(created_at__gt=since)

    return snaps


@router.post(
    path="/presigned-url",
    url_name="generate_presigned_url",
    response={HTTPStatus.OK: ImageUploadSchema},
    operation_id="generate_presigned_url",
)
def generate_presigned_url_for_upload(_request, payload: ImageUploadInput):
    object_name = f"{payload.id}/{uuid.uuid4()}-{payload.filename}"

    presigned_url = s3_client.generate_presigned_post_url(
        object_name, payload.content_type
    )

    return ImageUploadSchema(object_name=object_name, presigned_url=presigned_url)
