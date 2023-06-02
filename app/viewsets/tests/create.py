from http import HTTPStatus
from typing import Optional
from uuid import UUID

from django.db.models import Model
from django.urls import reverse
from requests import Response

from viewsets import utils
from viewsets.methods.create import CreateModelView
from viewsets.tests.abstract import AbstractModelViewTest, Credentials, Payloads


class CreateModelViewTest(AbstractModelViewTest):
    model_view = CreateModelView
    payloads: Payloads

    def __init__(self, payloads: Payloads, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.payloads = payloads

    def create_model(
        self, id: UUID, data: dict, credentials: Optional[dict]
    ) -> Response:
        if credentials is None:
            credentials = {}

        model_view: CreateModelView = self.get_model_view()
        model_name = utils.to_snake_case(self.model_view_set.model.__name__)
        if model_view.detail:
            related_model_name = utils.to_snake_case(model_view.model.__name__)
            url_name = f"{model_name}_{related_model_name}s"
            kwargs = {"id": id}
        else:
            url_name = f"{model_name}s"
            kwargs = {}

        return self.client.post(
            reverse(f"api:{url_name}", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: Response):
        self.test_case.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()

        model_view: CreateModelView = self.get_model_view()
        if model_view.detail:
            model = model_view.model
        else:
            model = self.model_view_set.model
        self.assert_content_equals_schema(
            content, model=model, output_schema=model_view.output_schema
        )

    def test_create_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.ok
        )
        self.assert_response_is_ok(response)

    def test_create_model_bad_request(self):
        if self.payloads.bad_request is None:
            self.test_case.skipTest("No bad request payload provided")
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.bad_request, credentials=credentials.ok
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.BAD_REQUEST
        )

    def test_create_model_conflict(self):
        if self.payloads.conflict is None:
            self.test_case.skipTest("No conflict payload provided")
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.conflict, credentials=credentials.ok
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.CONFLICT)

    def test_create_model_unauthorized(self):
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.ok, credentials=None
        )
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_create_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.create_model(
            id=instance.pk, data=self.payloads.ok, credentials=credentials.forbidden
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
