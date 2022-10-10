from http import HTTPStatus

from config.tests.base_test import BaseTest
from django.urls import reverse

from index.models import Index
from index.schemas import ExtendedIndexSchema, ValidationMode


class TestIndexes(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_create_index(self):
        data = {
            "name": "new-index",
            "validation_mode": ValidationMode.Manual,
            "description": "some description of this index",
        }
        kwargs = {}
        response = self.client.post(
            reverse("api:indexes", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        new_index = Index.objects.get(name="new-index")
        self.assertDictEqualsSchema(content, ExtendedIndexSchema.from_orm(new_index))
