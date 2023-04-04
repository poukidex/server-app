from http import HTTPStatus
from uuid import UUID

from ninja import Router

from config.exceptions import ForbiddenException, IncoherentInput
from core.enums import PendingPublicationStatus
from core.utils import check_object, update_object_from_schema
from index.models import PendingPublication, Publication
from index.schemas import PendingPublicationSchema, PublicationSchema, PublicationUpdate

router = Router()


@router.put(
    path="/{id}/accept",
    url_name="accept_pending_publication",
    response={HTTPStatus.CREATED: PublicationSchema},
    operation_id="accept_pending_item",
)
def accept_pending_publication(request, id: UUID):
    pending = (
        PendingPublication.objects.select_related("index")
        .select_for_update("status")
        .get(id=id)
    )

    if pending.index.creator != request.user:
        raise ForbiddenException()

    if pending.status != PendingPublicationStatus.PENDING:
        raise IncoherentInput(
            detail=["This publication has already been validated or refused"]
        )

    publication = Publication(
        index=pending.index,
        dominant_colors=pending.dominant_colors,
        name=pending.name,
        description=pending.description,
        object_name=pending.object_name,
    )
    check_object(publication)
    publication.save()

    pending.status = PendingPublicationStatus.ACCEPTED
    pending.save()

    return HTTPStatus.CREATED, publication


@router.put(
    path="/{id}/refuse",
    url_name="refuse_pending_publication",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="refuse_pending_item",
)
def refuse_pending_publication(request, id: UUID):
    pending = (
        PendingPublication.objects.select_related("index")
        .select_for_update("status")
        .get(id=id)
    )

    if pending.index.creator != request.user:
        raise ForbiddenException()

    if pending.status != PendingPublicationStatus.PENDING:
        raise IncoherentInput(
            detail=["This publication has already been validated or refused"]
        )

    pending.status = PendingPublicationStatus.REFUSED
    pending.save()

    return HTTPStatus.NO_CONTENT, None


@router.put(
    path="/{id}",
    url_name="pending_publication",
    response={HTTPStatus.OK: PendingPublicationSchema},
    operation_id="update_pending_item",
)
def update_pending_publication(request, id: UUID, payload: PublicationUpdate):
    pending = PendingPublication.objects.select_related("index").get(id=id)

    if request.user not in [pending.creator, pending.index.creator]:
        raise ForbiddenException()

    update_object_from_schema(pending, payload)

    return HTTPStatus.OK, pending


@router.delete(
    path="/{id}",
    url_name="pending_publication",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_pending_item",
)
def delete_pending_publication(request, id: UUID):
    pending = PendingPublication.objects.select_related("index").get(id=id)

    if request.user not in [pending.creator, pending.index.creator]:
        raise ForbiddenException()

    pending.delete()

    return HTTPStatus.NO_CONTENT, None
