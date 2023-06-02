from functools import wraps
from http import HTTPStatus
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import HttpRequest
from ninja import Router

from core.models.collections import Item, Snap
from core.schemas.collections import ItemInput, ItemOutput, SnapInput, SnapOutput
from viewsets.methods.abstract import ModelViewSet
from viewsets.methods.create import CreateModelView
from viewsets.methods.delete import DeleteModelView
from viewsets.methods.list import ListModelView
from viewsets.methods.retrieve import RetrieveModelView
from viewsets.methods.update import UpdateModelView

router = Router()


def user_is_collection_creator(func):
    @wraps(func)
    def wrapper(request, id, *args, **kwargs):
        item = Item.objects.get(id=id)
        if item.collection.creator != request.user:
            raise PermissionDenied()
        return func(request, id, *args, **kwargs)

    return wrapper


class ItemViewSet(ModelViewSet):
    model = Item
    input_schema = ItemInput
    output_schema = ItemOutput

    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        decorators=[user_is_collection_creator],
    )
    delete = DeleteModelView(decorators=[user_is_collection_creator])

    list_snaps = ListModelView(
        detail=True,
        model=Snap,
        output_schema=SnapOutput,
        queryset_getter=lambda request, id: Snap.objects.annotate(
            nb_likes=Count("likes", filter=Q(likes__liked=True)),
            nb_dislikes=Count("likes", filter=Q(likes__liked=False)),
        ).filter(item_id=id),
    )

    @staticmethod
    def pre_save_snap(instance: Snap, request: HttpRequest, id: UUID):
        instance.item_id = id
        instance.user = request.user

    create_snap = CreateModelView(
        detail=True,
        model=Snap,
        input_schema=SnapInput,
        output_schema=SnapOutput,
        pre_save=pre_save_snap,
    )


ItemViewSet.register_routes(router)


@router.get(
    path="/{id}/snap",
    url_name="my_snap",
    response={HTTPStatus.OK: SnapOutput},
    operation_id="retrieve_my_snap",
)
def retrieve_my_snap(request, id: UUID):
    return HTTPStatus.OK, Snap.objects.get(item_id=id, user=request.user)
