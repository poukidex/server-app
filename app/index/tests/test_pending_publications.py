from http import HTTPStatus

from django.urls import reverse

from config.tests.base_test import BaseTest
from core.enums import PendingPublicationStatus
from index.models import PendingPublication, Publication
from index.schemas import PendingPublicationSchema, PublicationSchema


class TestPendingPublications(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def _do_test_update_pending_publication(self, auth_user, expected_status):
        data = {
            "name": "new-name",
            "description": "description",
            "object_name": "some_object_name",
        }
        kwargs = {"id": self.second_index_pending_publication.id}
        response = self.client.put(
            reverse("api:pending_publication", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()

            publication_updated = PendingPublication.objects.get(
                id=self.second_index_pending_publication.id
            )

            self.assertDictEqualsSchema(
                content, PendingPublicationSchema.from_orm(publication_updated)
            )

    def test_update_pending_publication(self):
        self._do_test_update_pending_publication(self.auth_user_one, HTTPStatus.OK)

    def test_update_pending_publication_creator(self):
        self._do_test_update_pending_publication(self.auth_user_two, HTTPStatus.OK)

    def test_update_pending_publication_forbidden(self):
        self._do_test_update_pending_publication(
            self.auth_user_three, HTTPStatus.FORBIDDEN
        )

    def _do_test_delete_pending_publication(self, auth_user, expected_status):
        kwargs = {"id": self.second_index_pending_publication.id}
        response = self.client.delete(
            reverse("api:pending_publication", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.NO_CONTENT:
            self.assertFalse(
                PendingPublication.objects.filter(
                    id=self.second_index_pending_publication.id
                ).exists()
            )

    def test_delete_pending_publication(self):
        self._do_test_delete_pending_publication(
            self.auth_user_one, HTTPStatus.NO_CONTENT
        )

    def test_delete_pending_publication_creator(self):
        self._do_test_delete_pending_publication(
            self.auth_user_two, HTTPStatus.NO_CONTENT
        )

    def test_delete_pending_publication_forbidden(self):
        self._do_test_delete_pending_publication(
            self.auth_user_three, HTTPStatus.FORBIDDEN
        )

    def _do_test_accept_pending_publication(self, auth_user, expected_status):
        kwargs = {"id": self.second_index_pending_publication.id}
        response = self.client.put(
            reverse("api:accept_pending_publication", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.OK:
            content = response.json()
            publication = Publication.objects.get(
                name=self.second_index_pending_publication.name
            )
            self.assertDictEqualsSchema(
                content, PublicationSchema.from_orm(publication)
            )

            pending_publication = PendingPublication.objects.get(
                id=self.second_index_pending_publication.id
            )
            self.assertEqual(
                pending_publication.status, PendingPublicationStatus.ACCEPTED
            )

    def test_accept_pending_publication(self):
        self._do_test_accept_pending_publication(self.auth_user_one, HTTPStatus.CREATED)

    def test_accept_pending_publication_wrong_status(self):
        self.second_index_pending_publication.status = PendingPublicationStatus.ACCEPTED
        self.second_index_pending_publication.save()
        self._do_test_accept_pending_publication(
            self.auth_user_one, HTTPStatus.BAD_REQUEST
        )

    def test_accept_pending_publication_creator(self):
        self._do_test_accept_pending_publication(
            self.auth_user_two, HTTPStatus.FORBIDDEN
        )

    def _do_test_refuse_pending_publication(self, auth_user, expected_status):
        kwargs = {"id": self.second_index_pending_publication.id}
        response = self.client.put(
            reverse("api:refuse_pending_publication", kwargs=kwargs), **auth_user
        )
        self.assertEqual(response.status_code, expected_status)

        if expected_status == HTTPStatus.NO_CONTENT:
            self.assertFalse(
                Publication.objects.filter(
                    name=self.second_index_pending_publication.name
                ).exists()
            )
            pending_publication = PendingPublication.objects.get(
                id=self.second_index_pending_publication.id
            )
            self.assertEqual(
                pending_publication.status, PendingPublicationStatus.REFUSED
            )

    def test_refuse_pending_publication(self):
        self._do_test_refuse_pending_publication(
            self.auth_user_one, HTTPStatus.NO_CONTENT
        )

    def test_refuse_pending_publication_creator(self):
        self._do_test_refuse_pending_publication(
            self.auth_user_two, HTTPStatus.FORBIDDEN
        )

    def test_refuse_pending_publication_wrong_status(self):
        self.second_index_pending_publication.status = PendingPublicationStatus.ACCEPTED
        self.second_index_pending_publication.save()
        self._do_test_refuse_pending_publication(
            self.auth_user_one, HTTPStatus.BAD_REQUEST
        )
