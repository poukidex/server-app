from functools import wraps

from django.core.exceptions import PermissionDenied
from django.db.models import Count, QuerySet

from core.models.collections import Collection, Item
from core.schemas.collections import CollectionInput, CollectionOutput, ItemOutput
from viewsets.methods.abstract import APIViewSet
from viewsets.methods.create import CreateAPIView
from viewsets.methods.delete import DeleteAPIView
from viewsets.methods.list import ListAPIView
from viewsets.methods.retrieve import RetrieveAPIView
from viewsets.methods.update import UpdateAPIView


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

    def get_queryset(self, request) -> QuerySet[Collection]:
        return self.model.objects.annotate(nb_items=Count("items"))

    list = ListAPIView(output_schema=output_schema, queryset_getter=get_queryset)
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

    subsets = [
        APIViewSet(
            model=Item,
            list=ListAPIView(output_schema=ItemOutput),
        )
    ]
