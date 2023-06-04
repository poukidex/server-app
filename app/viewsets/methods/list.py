from http import HTTPStatus
from typing import Callable, List, Optional, Type
from uuid import UUID

from django.db.models import Model, QuerySet
from django.http import HttpRequest
from ninja import FilterSchema, Query, Router, Schema
from ninja.pagination import LimitOffsetPagination, paginate

from viewsets import utils
from viewsets.methods.abstract import AbstractModelView
from viewsets.utils import merge_decorators


class ListModelView(AbstractModelView):
    def __init__(
        self,
        output_schema: Type[Schema],
        query_schema: Type[FilterSchema] = None,
        queryset_getter: Callable[..., QuerySet[Model]] = None,
        model: Type[Model] = None,
        detail: bool = False,
        decorators: List[Callable] = None,
    ) -> None:
        super().__init__(decorators=decorators)
        self.output_schema = output_schema
        self.query_schema = query_schema
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
        query_schema = self.query_schema

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
            request: HttpRequest, filters: query_schema = Query(default=FilterSchema())
        ):
            return self.list_models(request=request, id=None, filters=filters)

    def register_instance_route(self, router: Router, model: Type[Model]) -> None:
        parent_model_name = utils.to_snake_case(model.__name__)
        model_name = utils.to_snake_case(self.model.__name__)
        plural_model_name = f"{model_name}s"
        url = "/{id}/" + plural_model_name
        operation_id = f"list_{parent_model_name}_{plural_model_name}"
        summary = f"List {self.model.__name__}s of a {model.__name__}"

        output_schema = self.output_schema
        query_schema = self.query_schema

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
            filters: query_schema = Query(default=FilterSchema()),
        ):
            return self.list_models(request=request, id=id, filters=filters)

    def list_models(
        self, request: HttpRequest, id: Optional[UUID], filters: FilterSchema
    ):
        if self.get_queryset is not None:
            if id is not None:
                queryset = self.get_queryset(request, id)
            else:
                queryset = self.get_queryset(request)
        else:
            queryset = self.model.objects.get_queryset()

        filters_dict = filters.dict()
        if "order_by" in filters_dict and filters_dict["order_by"] is not None:
            queryset = queryset.order_by(*filters_dict.pop("order_by"))

        queryset = filters.filter(queryset)
        return queryset
