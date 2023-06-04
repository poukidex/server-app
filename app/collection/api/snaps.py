from functools import wraps
from http import HTTPStatus
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpRequest
from ninja import Router

from core.models.collections import Like, Snap
from core.schemas.collections import (
    LikeInput,
    LikeOutput,
    LikeQuery,
    SnapInput,
    SnapOutput,
)
from core.schemas.common import OrderableQuery
from viewsets.methods.abstract import ModelViewSet
from viewsets.methods.delete import DeleteModelView
from viewsets.methods.list import ListModelView
from viewsets.methods.retrieve import RetrieveModelView
from viewsets.methods.update import UpdateModelView

router = Router()


def user_is_creator(func):
    @wraps(func)
    def wrapper(request: HttpRequest, id: UUID, *args, **kwargs):
        snap = Snap.objects.get(id=id)
        if snap.user != request.user:
            raise PermissionDenied()
        return func(request, id, *args, **kwargs)

    return wrapper


class SnapViewSet(ModelViewSet):
    model = Snap
    input_schema = SnapInput
    output_schema = SnapOutput

    list = ListModelView(
        output_schema=output_schema,
        query_schema=OrderableQuery,
        queryset_getter=lambda request, id: Snap.objects.select_related("user")
        .annotate(
            nb_likes=Count("likes", filter=Q(likes__liked=True)),
            nb_dislikes=Count("likes", filter=Q(likes__liked=False)),
        )
        .filter(item_id=id),
    )
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        decorators=[user_is_creator],
    )
    delete = DeleteModelView(decorators=[user_is_creator])

    list_likes = ListModelView(
        detail=True,
        model=Like,
        output_schema=LikeOutput,
        query_schema=LikeQuery,
        queryset_getter=lambda request, id: Snap.objects.filter(snap_id=id),
    )


SnapViewSet.register_routes(router)


@router.get(
    path="/{id}/like",
    url_name="snap_like",
    response={HTTPStatus.OK: LikeOutput},
    operation_id="retrieve_my_like",
)
def retrieve_my_like(request: HttpRequest, id: UUID):
    return HTTPStatus.OK, Like.objects.get(snap_id=id, user=request.user)


@router.post(
    path="/{id}/like",
    url_name="snap_like",
    response={HTTPStatus.OK: LikeOutput},
    operation_id="update_my_like",
)
def update_my_like(request: HttpRequest, id: UUID, payload: LikeInput):
    like, _ = Like.objects.get_or_create(snap_id=id, user=request.user)
    like.liked = payload.liked
    like.save()
    return HTTPStatus.OK, like


@router.delete(
    path="/{id}/like",
    url_name="snap_like",
    response={HTTPStatus.NO_CONTENT: None},
    operation_id="delete_my_like",
)
def delete_my_like(request: HttpRequest, id: UUID):
    like = Like.objects.get(snap_id=id, user=request.user)
    like.delete()
    return HTTPStatus.NO_CONTENT, None
