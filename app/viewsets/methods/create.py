from http import HTTPStatus
from typing import Callable, Type

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from viewsets import utils
from viewsets.methods.abstract import AbstractAPIView, APIViewSet
from viewsets.utils import merge_decorators


class CreateAPIView(AbstractAPIView):
    input_schema: Type[Schema]
    output_schema: Type[Schema]
    pre_save: Callable[[Model, HttpRequest], None]

    def __init__(
        self,
        input_schema: Type[Schema],
        output_schema: Type[Schema],
        pre_save: Callable = None,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.pre_save = pre_save

    def register_route(self, router: Router, model: Type[Model]) -> None:
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

    def sub_register_route(
        self, router: Router, model: Type[Model], parent: APIViewSet
    ) -> None:
        pass
