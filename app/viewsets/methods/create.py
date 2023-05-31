from http import HTTPStatus
from typing import Callable, Type
from uuid import UUID

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from viewsets import utils
from viewsets.methods.abstract import AbstractModelView
from viewsets.utils import merge_decorators


class CreateModelView(AbstractModelView):
    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        pre_save: Callable = None,
        model: Type[Model] = None,
        detail: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.pre_save = pre_save
        self.model = model
        self.detail = detail

    def register_route(self, router: Router, model: Type[Model]) -> None:
        if self.detail:
            self.register_instance_route(router, model)
        else:
            self.register_collection_route(router, model)

    def register_collection_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"create_{model_name}"
        summary = f"Create {model.__name__}"

        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.post(
            "/",
            response={HTTPStatus.CREATED: output_schema},
            url_name=f"{model_name}s",
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        def create_model(request: HttpRequest, payload: input_schema):
            instance = model()
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)
            if self.pre_save:
                self.pre_save(instance, request)
            instance.full_clean()
            instance.save()
            return HTTPStatus.CREATED, instance

    def register_instance_route(self, router: Router, model: Type[Model]) -> None:
        parent_model_name = utils.to_snake_case(model.__name__)
        model_name = utils.to_snake_case(self.model.__name__)
        plural_model_name = f"{model_name}s"
        url = "/{id}/" + plural_model_name
        operation_id = f"create_{parent_model_name}_{plural_model_name}"
        summary = f"Create {self.model.__name__} of a {model.__name__}"

        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.post(
            url,
            response={HTTPStatus.CREATED: output_schema},
            url_name=f"{parent_model_name}_{plural_model_name}",
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        def create_model(request: HttpRequest, id: UUID, payload: input_schema):
            instance = self.model()
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)
            if self.pre_save:
                self.pre_save(instance, request, id)
            instance.full_clean()
            instance.save()
            return HTTPStatus.CREATED, instance
