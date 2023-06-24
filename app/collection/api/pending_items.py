from http import HTTPStatus
from uuid import UUID

from ninja import Router

from core.enums import PendingItemStatus
from core.exceptions import ForbiddenException, IncoherentInput
from core.models.collections import Item, PendingItem
from core.schemas.collections import ItemOutput, ItemUpdate, PendingItemSchema

router = Router()


@router.put(
    path="/{id}/accept",
    url_name="accept_pending_item",
    response={HTTPStatus.CREATED: ItemOutput},
    operation_id="accept_pending_item",
)
def accept_pending_item(request, id: UUID):
    pending_item = (
        PendingItem.objects.select_related("collection")
        .select_for_update("status")
        .get(id=id)
    )

    if pending_item.collection.creator != request.user:
        raise ForbiddenException()

    if pending_item.status != PendingItemStatus.PENDING:
        raise IncoherentInput(
            detail=["This item has already been validated or refused"]
        )

    item = Item(
        collection=pending_item.collection,
        dominant_colors=pending_item.dominant_colors,
        name=pending_item.name,
        description=pending_item.description,
        object_name=pending_item.object_name,
    )
    item.full_clean()
    item.save()

    pending_item.status = PendingItemStatus.ACCEPTED
    pending_item.save()

    return HTTPStatus.CREATED, item


@router.put(
    path="/{id}/refuse",
    url_name="refuse_pending_item",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="refuse_pending_item",
)
def refuse_pending_item(request, id: UUID):
    pending_item = (
        PendingItem.objects.select_related("collection")
        .select_for_update("status")
        .get(id=id)
    )

    if pending_item.collection.creator != request.user:
        raise ForbiddenException()

    if pending_item.status != PendingItemStatus.PENDING:
        raise IncoherentInput(
            detail=["This item has already been validated or refused"]
        )

    pending_item.status = PendingItemStatus.REFUSED
    pending_item.save()

    return HTTPStatus.NO_CONTENT, None


@router.put(
    path="/{id}",
    url_name="pending_item",
    response={HTTPStatus.OK: PendingItemSchema},
    operation_id="update_pending_item",
)
def update_pending_item(request, id: UUID, payload: ItemUpdate):
    pending_item = PendingItem.objects.select_related("collection").get(id=id)

    if request.user not in [pending_item.creator, pending_item.collection.creator]:
        raise ForbiddenException()

    for attr, value in payload.dict().items():
        setattr(pending_item, attr, value)

    pending_item.full_clean()
    pending_item.save()
    return HTTPStatus.OK, pending_item


@router.delete(
    path="/{id}",
    url_name="pending_item",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_pending_item",
)
def delete_pending_item(request, id: UUID):
    pending_item = PendingItem.objects.select_related("collection").get(id=id)

    if request.user not in [pending_item.creator, pending_item.collection.creator]:
        raise ForbiddenException()

    pending_item.delete()

    return HTTPStatus.NO_CONTENT, None
