from http import HTTPStatus

from django.db.models import Count
from django.urls import reverse

from config.tests.base_test import BaseTest
from index.models import Index, PendingPublication, Publication
from index.schemas import (
    IndexSchema,
    PendingPublicationSchema,
    PublicationSchema,
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
        self.assertDictEqualsSchema(content, IndexSchema.from_orm(new_index))

    def test_retrieve_index(self):
        kwargs = {"id": self.first_index.id}
        response = self.client.get(
            reverse("api:index", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertDictEqualsSchema(content, IndexSchema.from_orm(self.first_index))

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

        self.assertDictEqualsSchema(content, IndexSchema.from_orm(index_updated))

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

    def _do_test_create_pending_publication(self, auth_user):
        data = {
            "name": "publication4",
            "description": "some description of this publication",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.first_index.id}
        response = self.client.post(
            reverse("api:index_pending_publications", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            PendingPublicationSchema.from_orm(
                PendingPublication.objects.get(id=content["id"])
            ),
        )

    def test_create_pending_publication_owner(self):
        self._do_test_create_pending_publication(self.auth_user_one)

    def test_create_pending_publication_user(self):
        self._do_test_create_pending_publication(self.auth_user_two)

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
            PublicationSchema.from_orm(Publication.objects.get(id=content["id"])),
        )

    def _do_test_list_pending_publications(self, auth_user, expected_number):
        kwargs = {"id": self.second_index.id}
        response = self.client.get(
            reverse("api:index_pending_publications", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), expected_number)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                PendingPublicationSchema.from_orm(
                    PendingPublication.objects.get(id=item["id"])
                ),
            )

    def test_list_pending_publications_owner(self):
        self._do_test_list_pending_publications(self.auth_user_one, 1)

    def test_list_pending_publications_creator(self):
        self._do_test_list_pending_publications(self.auth_user_two, 1)

    def test_list_pending_publications_user(self):
        self._do_test_list_pending_publications(self.auth_user_three, 0)

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
                PublicationSchema.from_orm(
                    Publication.objects.annotate(nb_captures=Count("propositions")).get(
                        id=item["id"]
                    )
                ),
            )
