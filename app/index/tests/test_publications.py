import uuid
from http import HTTPStatus

from config.tests.base_test import BaseTest
from django.db.models import Count
from django.urls import reverse

from index.models import Proposition, Publication
from index.schemas import ExtendedPropositionSchema, ExtendedPublicationSchema


class TestPublications(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_retrieve_publication(self):
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.get(
            reverse("api:publication", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        pub = Publication.objects.annotate(nb_captures=Count("propositions")).get(
            id=self.second_index_publication_2.id
        )
        self.assertDictEqualsSchema(content, ExtendedPublicationSchema.from_orm(pub))

    def test_update_publication(self):
        data = {"name": "new-name", "description": "description"}
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.put(
            reverse("api:publication", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        publication_updated = Publication.objects.get(
            id=self.second_index_publication_2.id
        )

        self.assertDictEqualsSchema(
            content, ExtendedPublicationSchema.from_orm(publication_updated)
        )

    def test_update_publication_forbidden(self):
        data = {"name": "new-name", "description": "description"}
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.put(
            reverse("api:publication", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_publication(self):
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.delete(
            reverse("api:publication", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(
            Publication.objects.filter(id=self.second_index_publication_2.id).exists()
        )

    def test_delete_publication_forbidden(self):
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.delete(
            reverse("api:publication", kwargs=kwargs), **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_create_proposition_unknown_publication(self):
        data = {
            "comment": "some comment of this proposition",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": uuid.uuid4()}
        response = self.client.post(
            reverse("api:publication_propositions", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_proposition(self):
        data = {
            "comment": "some comment of this proposition",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.second_index_publication_1.id}
        response = self.client.post(
            reverse("api:publication_propositions", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            ExtendedPropositionSchema.from_orm(
                Proposition.objects.get(id=content["id"])
            ),
        )

    def test_create_proposition_conflict(self):
        data = {
            "comment": "some comment of this proposition",
            "object_name": "an object_name somewhere",
        }
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.post(
            reverse("api:publication_propositions", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.CONFLICT)

    def test_list_propositions(self):
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.get(
            reverse("api:publication_propositions", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()["items"]
        self.assertEqual(len(content), 2)
        for item in content:
            self.assertDictEqualsSchema(
                item,
                ExtendedPropositionSchema.from_orm(
                    Proposition.objects.get(id=item["id"])
                ),
            )

    def test_generate_presigned_url_for_upload_publications(self):
        data = {"filename": "image.png", "content_type": "application/png"}

        kwargs = {"id": self.second_index_publication_1.id}
        response = self.client.post(
            reverse("api:publication_propositions_upload", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertIsNotNone(content["object_name"])
        self.assertIsNotNone(content["presigned_url"])

    def test_retrieve_my_proposition(self):
        kwargs = {"id": self.second_index_publication_2.id}
        response = self.client.get(
            reverse("api:my_proposition", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            ExtendedPropositionSchema.from_orm(
                self.second_index_publication_2_proposition_1
            ),
        )
