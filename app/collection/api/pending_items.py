from http import HTTPStatus
from uuid import UUID

from ninja import Router

from core.enums import PendingItemStatus
from core.exceptions import ForbiddenException, IncoherentInput
from core.models.collections import Item, PendingItem
from core.schemas.collections import ItemOutput, ItemUpdate, PendingItemSchema
from core.utils import check_object, update_object_from_schema

router = Router()


@router.put(
    path="/{id}/accept",
    url_name="accept_pending_item",
    response={HTTPStatus.CREATED: ItemOutput},
    operation_id="accept_pending_item",
)
def accept_pending_item(request, id: UUID):
    pending = (
        PendingItem.objects.select_related("collection")
        .select_for_update("status")
        .get(id=id)
    )

    if pending.collection.creator != request.user:
        raise ForbiddenException()

    if pending.status != PendingItemStatus.PENDING:
        raise IncoherentInput(
            detail=["This item has already been validated or refused"]
        )

    item = Item(
        collection=pending.collection,
        dominant_colors=pending.dominant_colors,
        name=pending.name,
        description=pending.description,
        object_name=pending.object_name,
    )
    check_object(item)
    item.save()

    pending.status = PendingItemStatus.ACCEPTED
    pending.save()

    return HTTPStatus.CREATED, item


@router.put(
    path="/{id}/refuse",
    url_name="refuse_pending_item",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="refuse_pending_item",
)
def refuse_pending_item(request, id: UUID):
    pending = (
        PendingItem.objects.select_related("collection")
        .select_for_update("status")
        .get(id=id)
    )

    if pending.collection.creator != request.user:
        raise ForbiddenException()

    if pending.status != PendingItemStatus.PENDING:
        raise IncoherentInput(
            detail=["This item has already been validated or refused"]
        )

    pending.status = PendingItemStatus.REFUSED
    pending.save()

    return HTTPStatus.NO_CONTENT, None


@router.put(
    path="/{id}",
    url_name="pending_item",
    response={HTTPStatus.OK: PendingItemSchema},
    operation_id="update_pending_item",
)
def update_pending_item(request, id: UUID, payload: ItemUpdate):
    pending = PendingItem.objects.select_related("collection").get(id=id)

    if request.user not in [pending.creator, pending.collection.creator]:
        raise ForbiddenException()

    update_object_from_schema(pending, payload)

    return HTTPStatus.OK, pending


@router.delete(
    path="/{id}",
    url_name="pending_item",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_pending_item",
)
def delete_pending_item(request, id: UUID):
    pending = PendingItem.objects.select_related("collection").get(id=id)

    if request.user not in [pending.creator, pending.collection.creator]:
        raise ForbiddenException()

    pending.delete()

    return HTTPStatus.NO_CONTENT, None
