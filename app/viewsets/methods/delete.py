from http import HTTPStatus
from typing import Type
from uuid import UUID

from django.db.models import Model
from django.http import HttpRequest
from ninja import Router

from viewsets import utils
from viewsets.methods.abstract import AbstractModelView, ModelViewSet
from viewsets.utils import merge_decorators


class DeleteModelView(AbstractModelView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def register_route(self, router: Router, model: Type[Model]) -> None:
        model_name = utils.to_snake_case(model.__name__)
        operation_id = f"delete_{model_name}"
        summary = f"Delete {model.__name__}"

        @router.delete(
            "/{id}",
            response={HTTPStatus.NO_CONTENT: None},
            url_name=model_name,
            operation_id=operation_id,
            summary=summary,
        )
        @merge_decorators(self.decorators)
        def delete_model(request: HttpRequest, id: UUID):
            instance = model.objects.get(pk=id)
            instance.delete()
            return HTTPStatus.NO_CONTENT, None

    def sub_register_route(
        self, router: Router, model: Type[Model], parent: ModelViewSet
    ) -> None:
        pass
