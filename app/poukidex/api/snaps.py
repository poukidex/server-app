from http import HTTPStatus
from uuid import UUID

from django.db.models import Count, Q
from ninja import Query, Router, Schema
from ninja.pagination import paginate

from config.exceptions import ForbiddenException
from config.pagination import OverpoweredPagination
from core.utils import update_object_from_schema
from poukidex.models import Like, Snap
from poukidex.schemas import LikeInput, LikeQuery, LikeSchema, SnapSchema, SnapUpdate

router = Router()


@router.get(
    path="/{id}",
    url_name="snap",
    response={HTTPStatus.OK: SnapSchema},
    operation_id="get_capture",
)
def retrieve_snap(request, id: UUID):
    return HTTPStatus.OK, Snap.objects.annotate(
        nb_likes=Count("likes", filter=Q(likes__liked=True)),
        nb_dislikes=Count("likes", filter=Q(likes__liked=False)),
    ).get(id=id)


@router.put(
    path="/{id}",
    url_name="snap",
    response={HTTPStatus.OK: SnapSchema},
    operation_id="update_capture",
)
def update_snap(request, id: UUID, payload: SnapUpdate):
    snap: Snap = Snap.objects.select_related("item__collection").get(id=id)

    if snap.user != request.user and snap.item.collection.creator != request.user:
        raise ForbiddenException()

    update_object_from_schema(snap, payload)

    return HTTPStatus.OK, snap


@router.delete(
    path="/{id}",
    url_name="snap",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_capture",
)
def delete_snap(request, id: UUID):
    snap: Snap = Snap.objects.select_related("item__collection").get(id=id)

    if snap.user != request.user and snap.item.collection.creator != request.user:
        raise ForbiddenException()

    snap.delete()

    return HTTPStatus.NO_CONTENT, None


@router.post(
    path="/{id}/likes",
    url_name="snap_likes",
    response={HTTPStatus.OK: LikeSchema},
    operation_id="like_snap",
)
def like_snap(request, id: UUID, payload: LikeInput):
    snap: Snap = Snap.objects.select_related("item__collection").get(id=id)

    approbation, _ = Like.objects.get_or_create(snap=snap, user=request.user)
    approbation.liked = payload.liked
    approbation.save()

    return HTTPStatus.OK, approbation


@router.get(
    path="/{id}/likes",
    url_name="snap_likes",
    response={HTTPStatus.OK: list[LikeSchema]},
    operation_id="get_like_list",
)
@paginate(OverpoweredPagination)
def list_likes(request, id: UUID, filters: LikeQuery = Query(default=Schema())):
    filters_dict: dict = filters.dict(exclude_unset=True)
    return Like.objects.filter(snap_id=id, **filters_dict)


@router.get(
    path="/{id}/like",
    url_name="snap_like",
    response={HTTPStatus.OK: LikeSchema},
    operation_id="get_my_like",
)
def get_like(request, id: UUID):
    return HTTPStatus.OK, Like.objects.get(snap_id=id, user=request.user)


@router.delete(
    path="/{id}/like",
    url_name="snap_like",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_like",
)
def delete_like(request, id: UUID):
    approbation: Like = Like.objects.get(snap_id=id, user=request.user)

    approbation.delete()

    return HTTPStatus.NO_CONTENT, None
