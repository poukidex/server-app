import uuid
from http import HTTPStatus
from typing import Optional
from uuid import UUID

from django.db.models import Model
from django.urls import reverse
from requests import Response

from viewsets import utils
from viewsets.methods.delete import DeleteModelView
from viewsets.tests.abstract import AbstractModelViewTest, Credentials


class DeleteModelViewTest(AbstractModelViewTest):
    model_view = DeleteModelView

    def delete_model(self, id: UUID, credentials: Optional[dict]) -> Response:
        if credentials is None:
            credentials = {}

        kwargs = {"id": id}
        url_name = utils.to_snake_case(self.api.model.__name__)
        return self.client.delete(
            reverse(f"api:{url_name}", kwargs=kwargs),
            content_type="application/json",
            **credentials,
        )

    def assert_response_is_ok(self, response: Response):
        self.test_case.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.test_case.assertEqual(response.content, b"")

    def test_delete_model_ok(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        instance: Model = self.get_instance(self.test_case)
        response = self.delete_model(id=instance.pk, credentials=credentials.ok)
        self.assert_response_is_ok(response)

    def test_delete_model_unauthorized(self):
        instance: Model = self.get_instance(self.test_case)
        response = self.delete_model(id=instance.pk, credentials=None)
        self.assert_response_is_bad_request(
            response, status_code=HTTPStatus.UNAUTHORIZED
        )

    def test_delete_model_not_found(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        response = self.delete_model(id=uuid.uuid4(), credentials=credentials.ok)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.NOT_FOUND)

    def test_delete_model_forbidden(self):
        credentials: Credentials = self.get_credentials(self.test_case)
        if credentials.forbidden is None:
            self.test_case.skipTest("No forbidden credentials provided")
        instance: Model = self.get_instance(self.test_case)
        response = self.delete_model(id=instance.pk, credentials=credentials.forbidden)
        self.assert_response_is_bad_request(response, status_code=HTTPStatus.FORBIDDEN)
