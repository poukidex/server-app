from http import HTTPStatus
from typing import Callable, List, Type
from uuid import UUID

from django.db.models import Model
from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.pagination import LimitOffsetPagination, paginate

from viewsets import utils
from viewsets.methods.abstract import AbstractAPIView
from viewsets.utils import merge_decorators


class ListAPIView(AbstractAPIView):
    def __init__(
        self,
        output_schema: Type[Schema],
        filter_schema: Type[FilterSchema] = None,
        queryset_getter: Callable = None,
        model: Type[Model] = None,
        detail: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.output_schema = output_schema
        self.filter_schema = filter_schema
        self.get_queryset = queryset_getter
        self.model = model
        self.detail = detail

    def register_route(self, router: Router, model: Type[Model]) -> None:
        if self.detail:
            self.register_instance_route(router, model)
        else:
            self.register_collection_route(router, model)

    def register_collection_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"list_{model_name}s"
        summary = f"List {model.__name__}s"

        output_schema = self.output_schema
        filter_schema = self.filter_schema

        @router.get(
            "/",
            response={HTTPStatus.OK: List[output_schema]},
            url_name=f"{model_name}s",
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        @paginate(LimitOffsetPagination)
        def list_models(
            request: HttpRequest, filters: filter_schema = Query(default=FilterSchema())
        ):
            if self.get_queryset is not None:
                queryset = self.get_queryset(request)
            else:
                queryset = model.objects.get_queryset()
            queryset = filters.filter(queryset)
            return queryset

    def register_instance_route(self, router: Router, model: Type[Model]) -> None:
        parent_model_name = utils.to_snake_case(model.__name__)
        model_name = utils.to_snake_case(self.model.__name__)
        plural_model_name = f"{model_name}s"
        url = "/{id}/" + plural_model_name
        operation_id = f"list_{parent_model_name}_{plural_model_name}"
        summary = f"List {self.model.__name__}s of a {model.__name__}"

        output_schema = self.output_schema
        filter_schema = self.filter_schema

        @router.get(
            url,
            response={HTTPStatus.OK: List[output_schema]},
            url_name=f"{parent_model_name}_{plural_model_name}",
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        @paginate(LimitOffsetPagination)
        def list_models(
            request: HttpRequest,
            id: UUID,
            filters: filter_schema = Query(default=FilterSchema()),
        ):
            if self.get_queryset is not None:
                queryset = self.get_queryset(request, id)
            else:
                queryset = self.model.objects.get_queryset()
            queryset = filters.filter(queryset)
            return queryset
