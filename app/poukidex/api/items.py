from http import HTTPStatus
from uuid import UUID

from django.db.models import Count, Q
from ninja import Router
from ninja.pagination import paginate

from config.exceptions import ForbiddenException
from config.pagination import OverpoweredPagination
from core.utils import check_object, update_object_from_schema
from poukidex.models import Item, Snap
from poukidex.schemas import ItemSchema, ItemUpdate, SnapInput, SnapSchema

router = Router()


@router.get(
    path="/{id}",
    url_name="item",
    response={HTTPStatus.OK: ItemSchema},
    operation_id="get_item",
)
def retrieve_item(request, id: UUID):
    return HTTPStatus.OK, Item.objects.annotate(nb_snaps=Count("snaps")).get(id=id)


@router.put(
    path="/{id}",
    url_name="item",
    response={HTTPStatus.OK: ItemSchema},
    operation_id="update_item",
)
def update_item(request, id: UUID, payload: ItemUpdate):
    item: Item = Item.objects.select_related("collection").get(id=id)

    if item.collection.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(item, payload)

    return HTTPStatus.OK, item


@router.delete(
    path="/{id}",
    url_name="item",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_item",
)
def delete_item(request, id: UUID):
    item: Item = Item.objects.select_related("collection").get(id=id)

    if item.collection.creator != request.user:
        raise ForbiddenException()

    item.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/snaps",
    url_name="item_snaps",
    response={HTTPStatus.CREATED: SnapSchema},
    operation_id="create_capture",
)
def add_snap(request, id: UUID, payload: SnapInput):
    # Assert item exists
    Item.objects.get(id=id)

    snap: Snap = Snap(item_id=id, user=request.user, **payload.dict())

    check_object(snap)

    snap.save()

    return HTTPStatus.CREATED, snap


@router.get(
    path="/{id}/snap",
    url_name="my_snap",
    response={HTTPStatus.OK: SnapSchema},
    operation_id="get_my_capture",
)
def retrieve_my_snap(request, id: UUID):
    return HTTPStatus.OK, Snap.objects.get(item_id=id, user=request.user)


@router.get(
    path="/{id}/snaps",
    url_name="item_snaps",
    response={HTTPStatus.OK: list[SnapSchema]},
    operation_id="get_capture_list",
)
@paginate(OverpoweredPagination)
def list_snaps(request, id: UUID):
    return Snap.objects.annotate(
        nb_likes=Count("likes", filter=Q(likes__liked=True)),
    ).filter(item_id=id)
