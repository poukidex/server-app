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
from viewsets.methods.abstract import APIViewSet
from viewsets.methods.create import CreateAPIView
from viewsets.methods.delete import DeleteAPIView
from viewsets.methods.list import ListAPIView
from viewsets.methods.retrieve import RetrieveAPIView
from viewsets.methods.update import UpdateAPIView

router = Router()


def user_is_creator(func):
    @wraps(func)
    def wrapper(request, id, *args, **kwargs):
        collection = Collection.objects.get(id=id)
        if collection.creator != request.user:
            raise PermissionDenied()
        return func(request, id, *args, **kwargs)

    return wrapper


class CollectionAPI(APIViewSet):
    model = Collection
    input_schema = CollectionInput
    output_schema = CollectionOutput

    list = ListAPIView(
        output_schema=output_schema,
        queryset_getter=lambda request: Collection.objects.annotate(
            nb_items=Count("items")
        ),
    )
    create = CreateAPIView(
        input_schema=input_schema,
        output_schema=output_schema,
        pre_save=lambda instance, request: setattr(instance, "creator", request.user),
    )
    retrieve = RetrieveAPIView(output_schema=output_schema)
    update = UpdateAPIView(
        input_schema=input_schema,
        output_schema=output_schema,
        decorators=[user_is_creator],
    )
    delete = DeleteAPIView(decorators=[user_is_creator])

    list_items = ListAPIView(
        detail=True,
        model=Item,
        output_schema=ItemOutput,
        queryset_getter=lambda request, id: Item.objects.filter(collection_id=id),
    )
    create_item = CreateAPIView(
        detail=True,
        model=Item,
        input_schema=ItemInput,
        output_schema=ItemOutput,
        pre_save=lambda instance, request, id: setattr(instance, "collection_id", id),
        decorators=[user_is_creator],
    )


CollectionAPI.register_routes(router)
