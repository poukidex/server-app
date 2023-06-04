from http import HTTPStatus
from typing import Optional
from uuid import UUID

from django.db.models import Model
from django.urls import reverse
from requests import Response

from viewsets import utils
from viewsets.methods.list import ListModelView
from viewsets.tests.abstract import AbstractModelViewTest, Credentials


class ListModelViewTest(AbstractModelViewTest):
    model_view = ListModelView

    def list_model(self, id: UUID, credentials: Optional[dict]) -> Response:
        if credentials is None:
            credentials = {}

        model_view: ListModelView = self.get_model_view()
        model_name = utils.to_snake_case(self.model_view_set.model.__name__)
        if model_view.detail:
            related_model_name = utils.to_snake_case(model_view.model.__name__)
            url_name = f"{model_name}_{related_model_name}s"
            kwargs = {"id": id}
        else:
            url_name = f"{model_name}s"
            kwargs = {}

        return self.client.get(
            reverse(f"api:{url_name}", kwargs=kwargs),
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: Response, id: UUID):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        model_view: ListModelView = self.get_model_view()

        # TODO: Refactor get_queryset in abstract.py
        if model_view.get_queryset is not None:
            if model_view.detail:
                queryset = model_view.get_queryset(None, id)
            else:
                queryset = model_view.get_queryset(None)
        else:
            queryset = self.model_view_set.model.objects.get_queryset()

        # TODO: Add support for order_by and other filters
        # filters_dict = filters.dict()
        # if "order_by" in filters_dict and filters_dict["order_by"] is not None:
        #     queryset = queryset.order_by(*filters_dict.pop("order_by"))

        self.assert_content_equals_schema_list(
            content, queryset=queryset, output_schema=model_view.output_schema
        )

    def test_list_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(id=instance.pk, credentials=credentials.ok)
        self.assert_response_is_ok(response, id=instance.pk)

    def test_list_model_unauthorized(self):
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(id=instance.pk, credentials=None)
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_list_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.list_model(id=instance.pk, credentials=credentials.forbidden)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
