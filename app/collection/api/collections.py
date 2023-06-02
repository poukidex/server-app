from functools import wraps

from django.core.exceptions import PermissionDenied
from django.db.models import Count
from ninja import Router

from core.models.collections import Collection, Item
from core.schemas.collections import (
    CollectionInput,
    CollectionOutput,
    ItemInput,
    ItemOutput,
)
from viewsets.methods.abstract import ModelViewSet
from viewsets.methods.create import CreateModelView
from viewsets.methods.delete import DeleteModelView
from viewsets.methods.list import ListModelView
from viewsets.methods.retrieve import RetrieveModelView
from viewsets.methods.update import UpdateModelView

router = Router()


def user_is_creator(func):
    @wraps(func)
    def wrapper(request, id, *args, **kwargs):
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
        queryset_getter=lambda request: Collection.objects.annotate(
            nb_items=Count("items")
        ),
    )
    create = CreateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        pre_save=lambda instance, request: setattr(instance, "creator", request.user),
    )
    retrieve = RetrieveModelView(output_schema=output_schema)
    update = UpdateModelView(
        input_schema=input_schema,
        output_schema=output_schema,
        decorators=[user_is_creator],
    )
    delete = DeleteModelView(decorators=[user_is_creator])

    list_items = ListModelView(
        detail=True,
        model=Item,
        output_schema=ItemOutput,
        queryset_getter=lambda request, id: Item.objects.filter(collection_id=id),
    )
    create_item = CreateModelView(
        detail=True,
        model=Item,
        input_schema=ItemInput,
        output_schema=ItemOutput,
        pre_save=lambda instance, request, id: setattr(instance, "collection_id", id),
        decorators=[user_is_creator],
    )


CollectionViewSet.register_routes(router)