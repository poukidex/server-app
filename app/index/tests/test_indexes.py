from http import HTTPStatus

from config.tests.base_test import BaseTest
from django.db.models import Count
from django.urls import reverse

from index.models import Index, Publication
from index.schemas import (
    ExtendedIndexSchema,
    ExtendedPublicationSchema,
    IndexSchema,
    ValidationMode,
)


class TestIndexes(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_list_indexes(self):
        kwargs = {}
        response = self.client.get(
            reverse("api:indexes", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), 2)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                IndexSchema.from_orm(
                    Index.objects.annotate(nb_items=Count("publications")).get(
                        id=item["id"]
                    )
                ),
            )

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

    def test_retrieve_index(self):
        kwargs = {"id": self.first_index.id}
        response = self.client.get(
            reverse("api:index", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertDictEqualsSchema(
            content, ExtendedIndexSchema.from_orm(self.first_index)
        )

    def test_update_index(self):
        data = {"name": "new-name", "description": "description"}
        kwargs = {"id": self.first_index.id}
        response = self.client.put(
            reverse("api:index", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        index_updated = Index.objects.get(id=self.first_index.id)

        self.assertDictEqualsSchema(
            content, ExtendedIndexSchema.from_orm(index_updated)
        )

    def test_update_index_forbidden(self):
        data = {"name": "new-name", "description": "description"}
        kwargs = {"id": self.first_index.id}
        response = self.client.put(
            reverse("api:index", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_index(self):
        kwargs = {"id": self.first_index.id}
        response = self.client.delete(
            reverse("api:index", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(Index.objects.filter(id=self.first_index.id).exists())

    def test_delete_index_forbidden(self):
        kwargs = {"id": self.first_index.id}
        response = self.client.delete(
            reverse("api:index", kwargs=kwargs), **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_create_publication(self):
        data = {
            "name": "publication1",
            "description": "some description of this publication",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.first_index.id}
        response = self.client.post(
            reverse("api:index_publications", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            ExtendedPublicationSchema.from_orm(
                Publication.objects.get(id=content["id"])
            ),
        )

    def test_create_publication_forbidden(self):
        data = {
            "name": "publication1",
            "description": "some description of this publication",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.first_index.id}
        response = self.client.post(
            reverse("api:index_publications", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_list_publications(self):
        kwargs = {"id": self.second_index.id}
        response = self.client.get(
            reverse("api:index_publications", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), 2)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                ExtendedPublicationSchema.from_orm(
                    Publication.objects.get(id=item["id"])
                ),
            )

    def test_generate_presigned_url_for_upload_indexes(self):
        data = {"filename": "image.png", "content_type": "application/png"}

        kwargs = {"id": self.second_index.id}
        response = self.client.post(
            reverse("api:index_publications_upload", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertIsNotNone(content["object_name"])
        self.assertIsNotNone(content["presigned_url"])
