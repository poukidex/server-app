from http import HTTPStatus
from typing import Type
from uuid import UUID

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router, Schema

from viewsets import utils
from viewsets.methods.abstract import AbstractModelView
from viewsets.utils import merge_decorators


class UpdateModelView(AbstractModelView):
    input_schema: Type[Schema]
    output_schema: Type[Schema]

    def __init__(
        self, input_schema: Type[Schema], output_schema: Type[Schema], *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.input_schema = input_schema
        self.output_schema = output_schema

    def register_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"update_{model_name}"
        summary = f"Update {model.__name__}"

        input_schema = self.input_schema
        output_schema = self.output_schema

        @router.put(
            "/{id}",
            response={HTTPStatus.OK: output_schema},
            url_name=model_name,
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        def update_model(request: HttpRequest, id: UUID, payload: input_schema):
            instance = model.objects.get(pk=id)
            for field, value in payload.dict(exclude_unset=True).items():
                setattr(instance, field, value)
            instance.full_clean()
            instance.save()
            return HTTPStatus.OK, instance
