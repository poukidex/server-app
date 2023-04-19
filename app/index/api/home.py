import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Optional

from django.db.models import Count, Q
from ninja import Router
from ninja.pagination import paginate

from config.external_client import s3_client
from config.pagination import OverpoweredPagination
from core.schemas import ImageUploadInput, ImageUploadSchema
from index.models import Proposition
from index.schemas import PropositionSchema

router = Router()


@router.get(
    path="/feed",
    url_name="feed",
    response={HTTPStatus.OK: list[PropositionSchema]},
    operation_id="get_feed",
)
@paginate(OverpoweredPagination)
def retrieve_feed(request, since: Optional[datetime] = None):
    propositions = Proposition.objects.select_related("publication__index").annotate(
        nb_likes=Count("approbations", filter=Q(approbations__approved=True)),
    )

    if since:
        propositions = propositions.filter(created_at__gt=since)

    return propositions


@router.post(
    path="/presigned-url",
    url_name="generate_presigned_url",
    response={HTTPStatus.OK: ImageUploadSchema},
    operation_id="generate_presigned_url",
)
def generate_presigned_url_for_upload(request, payload: ImageUploadInput):
    object_name = f"{payload.id}/{uuid.uuid4()}-{payload.filename}"

    presigned_url = s3_client.generate_presigned_post_url(
        object_name, payload.content_type
    )

    return ImageUploadSchema(object_name=object_name, presigned_url=presigned_url)