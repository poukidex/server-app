from http import HTTPStatus
from typing import Callable, Optional, Type
from uuid import UUID

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from viewsets import utils
from viewsets.methods.abstract import AbstractAPIView, APIViewSet
from viewsets.utils import merge_decorators


class RetrieveAPIView(AbstractAPIView):
    output_schema: Type[Schema]
    get_queryset: Optional[Callable]

    def __init__(
        self,
        output_schema: Type[Schema],
        queryset_getter: Callable = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.output_schema = output_schema
        self.get_queryset = queryset_getter

    def register_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"retrieve_{model_name}"
        summary = f"Retrieve {model.__name__}"

        output_schema = self.output_schema

        @router.get(
            "/{id}",
            response={HTTPStatus.OK: output_schema},
            url_name=model_name,
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        def retrieve_model(request: HttpRequest, id: UUID):
            if self.get_queryset is not None:
                queryset = self.get_queryset(request, id)
            else:
                queryset = model.objects.get_queryset()
            instance = queryset.get(pk=id)
            return HTTPStatus.OK, instance

    def sub_register_route(
        self, router: Router, model: Type[Model], parent: APIViewSet
    ) -> None:
        pass
