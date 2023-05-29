import uuid
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from django.db.models import Model
from django.urls import reverse
from requests import Response

from viewsets import utils
from viewsets.methods.retrieve import RetrieveAPIView
from viewsets.tests.abstract import AbstractAPIViewTest, Credentials


class RetrieveAPIViewTest(AbstractAPIViewTest):
    api_view_cls = RetrieveAPIView

    def retrieve_model(self, id: UUID, credentials: Optional[dict]) -> Response:
        if credentials is None:
            credentials = {}

        kwargs = {"id": id}
        url_name = utils.to_snake_case(self.api.model.__name__)
        return self.client.get(
            reverse(f"api:{url_name}", kwargs=kwargs),
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: Response):
        self.test_case.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        method: RetrieveAPIView = self.get_api_view()
        self.assert_content_equals_schema(
            content, model=self.api.model, output_schema=method.output_schema
        )

    def test_retrieve_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.retrieve_model(id=instance.pk, credentials=credentials.ok)
        self.assert_response_is_ok(response)

    def test_retrieve_model_unauthorized(self):
        instance: Model = self.get_instance(self.test_case)
        response = self.retrieve_model(id=instance.pk, credentials=None)
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_retrieve_model_not_found(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        response = self.retrieve_model(id=uuid.uuid4(), credentials=credentials.ok)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)

    def test_retrieve_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.retrieve_model(
            id=instance.pk, credentials=credentials.forbidden
        )
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
