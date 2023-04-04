from http import HTTPStatus
from uuid import UUID

from django.db.models import Count
from ninja import Router
from ninja.pagination import paginate

from config.exceptions import ForbiddenException
from config.pagination import OverpoweredPagination
from core.utils import check_object, update_object_from_schema
from poukidex.models import Collection, Item, PendingItem
from poukidex.schemas import (
    CollectionInput,
    CollectionSchema,
    CollectionUpdate,
    ItemInput,
    ItemSchema,
    PendingItemSchema,
)

router = Router()


@router.get(
    path="",
    response={HTTPStatus.OK: list[CollectionSchema]},
    url_name="collections",
    operation_id="get_collection_list",
    summary="List all collections",
)
@paginate(OverpoweredPagination)
def list_collections(_):
    return Collection.objects.annotate(nb_items=Count("items")).all()


@router.post(
    path="",
    response={HTTPStatus.CREATED: CollectionSchema},
    url_name="collections",
    operation_id="create_collection",
    summary="Create a collection",
)
def create_collection(request, payload: CollectionInput):
    collection = Collection(creator=request.user, **payload.dict())
    check_object(collection)
    collection.save()
    return HTTPStatus.CREATED, collection


@router.get(
    path="/{id}",
    response={HTTPStatus.OK: CollectionSchema},
    url_name="collection",
    operation_id="get_collection",
    summary="Get collection",
)
def get_collection(_, id: UUID):
    return HTTPStatus.OK, Collection.objects.annotate(nb_items=Count("items")).get(
        id=id
    )


@router.put(
    path="/{id}",
    response={HTTPStatus.OK: CollectionSchema},
    url_name="collection",
    operation_id="update_collection",
    summary="Update collection",
)
def update_collection(request, id: UUID, payload: CollectionUpdate):
    collection = Collection.objects.get(id=id)

    if collection.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(collection, payload)

    return HTTPStatus.OK, collection


@router.delete(
    path="/{id}",
    response={HTTPStatus.NO_CONTENT: None},
    url_name="collection",
    operation_id="delete_collection",
    summary="Delete a collection",
)
def delete_collection(request, id: UUID):
    collection = Collection.objects.get(id=id)

    if collection.creator != request.user:
        raise ForbiddenException()

    collection.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/pending-items",
    response={HTTPStatus.CREATED: PendingItemSchema},
    url_name="collection_pending_items",
    operation_id="create_pending_item",
)
def create_pending_item(request, id: UUID, payload: ItemInput):
    collection = Collection.objects.get(id=id)

    pending_item = PendingItem(
        collection=collection, creator=request.user, **payload.dict()
    )

    check_object(pending_item)

    pending_item.save()

    return HTTPStatus.CREATED, pending_item


@router.get(
    path="/{id}/pending-items",
    response={HTTPStatus.OK: list[PendingItemSchema]},
    url_name="collection_pending_items",
    operation_id="get_pending_items_list",
    summary="List pending items of collection",
)
@paginate(OverpoweredPagination)
def list_pending_items(request, id: UUID):
    collection = Collection.objects.get(id=id)

    if request.user == collection.creator:
        return PendingItem.objects.filter(collection=collection)
    else:
        return PendingItem.objects.filter(collection=collection, creator=request.user)


@router.post(
    path="/{id}/items",
    response={HTTPStatus.CREATED: ItemSchema},
    url_name="collection_items",
    operation_id="create_item",
)
def create_item(request, id: UUID, payload: ItemInput):
    collection = Collection.objects.get(id=id)

    if collection.creator != request.user:
        raise ForbiddenException()

    item = Item(collection=collection, **payload.dict())
    check_object(item)
    item.save()
    return HTTPStatus.CREATED, item


@router.get(
    path="/{id}/items",
    response={HTTPStatus.OK: list[ItemSchema]},
    url_name="collection_items",
    operation_id="get_item_list",
)
@paginate(OverpoweredPagination)
def list_items(_, id: UUID):
    return Item.objects.annotate(nb_snaps=Count("snaps")).filter(collection_id=id)
