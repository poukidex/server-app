from functools import wraps
from uuid import UUID

from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpRequest
from ninja import Router
from ninja_crud.views import (
    CreateModelView,
    DeleteModelView,
    ListModelView,
    ModelViewSet,
    RetrieveModelView,
    UpdateModelView,
)

from core.models.collections import Collection, Item
from core.schemas.collections import (
    CollectionInput,
    CollectionOutput,
    ItemInput,
    ItemOutput,
)
from core.schemas.common import OrderableQuery

router = Router()


def user_is_creator(func):
    @wraps(func)
    def wrapper(request: HttpRequest, id: UUID, *args, **kwargs):
        collection = Collection.objects.get(id=id)
        if collection.creator != request.user:
            raise PermissionDenied()
        return func(request, id, *args, **kwargs)

    return wrapper


class CollectionViewSet(ModelViewSet):
    model = Collection
    input_schema = CollectionInput
    output_schema = CollectionOutput

    list = ListModelView(
        output_schema=output_schema,
        filter_schema=OrderableQuery,
        queryset_getter=lambda: Collection.objects.annotate(nb_items=Count("items")),
    )
    create = CreateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        pre_save=lambda request, instance: setattr(instance, "creator", request.user),
    )
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        decorators=[user_is_creator],
    )
    delete = DeleteModelView(decorators=[user_is_creator])

    list_items = ListModelView(
        is_instance_view=True,
        related_model=Item,
        output_schema=ItemOutput,
        queryset_getter=lambda id: Item.objects.filter(collection_id=id),
    )
    create_item = CreateModelView(
        is_instance_view=True,
        related_model=Item,
        input_schema=ItemInput,
        output_schema=ItemOutput,
        pre_save=lambda request, id, instance: setattr(instance, "collection_id", id),
        decorators=[user_is_creator],
    )


CollectionViewSet.register_routes(router)
