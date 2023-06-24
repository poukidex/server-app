from http import HTTPStatus

from django.urls import reverse

from core.tests.base import BaseTest


class ObjectStorageViewSetTest(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_generate_presigned_url(self):
        data = {
            "id": self.collection_1.id,
            "filename": "image.png",
            "content_type": "application/png",
        }

        kwargs = {}
        response = self.client.post(
            reverse("api:generate_presigned_url", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertIsNotNone(content["object_name"])
        self.assertIsNotNone(content["presigned_url"])
