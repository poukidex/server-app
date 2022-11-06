from http import HTTPStatus

from config.tests.base_test import BaseTest
from django.urls import reverse

from index.models import Approbation, Proposition, Publication
from index.schemas import ExtendedPropositionSchema


class TestPropostions(BaseTest):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_retrieve_proposition(self):
        kwargs = {"id": self.second_index_publication_2_proposition_2.id}
        response = self.client.get(
            reverse("api:proposition", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()
        self.assertDictEqualsSchema(
            content,
            ExtendedPropositionSchema.from_orm(
                self.second_index_publication_2_proposition_2
            ),
        )

    def test_update_proposition(self):
        data = {"comment": "some comment"}
        kwargs = {"id": self.second_index_publication_2_proposition_1.id}
        response = self.client.put(
            reverse("api:proposition", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        content = response.json()

        proposition_updated = Proposition.objects.get(
            id=self.second_index_publication_2_proposition_1.id
        )

        self.assertDictEqualsSchema(
            content, ExtendedPropositionSchema.from_orm(proposition_updated)
        )

    def test_update_proposition_forbidden(self):
        data = {"comment": "some comment"}
        kwargs = {"id": self.second_index_publication_2_proposition_2.id}
        response = self.client.put(
            reverse("api:proposition", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_delete_proposition(self):
        kwargs = {"id": self.second_index_publication_2_proposition_1.id}
        response = self.client.delete(
            reverse("api:proposition", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(
            Publication.objects.filter(
                id=self.second_index_publication_2_proposition_1.id
            ).exists()
        )

    def test_delete_proposition_by_creator(self):
        kwargs = {"id": self.second_index_publication_2_proposition_2.id}
        response = self.client.delete(
            reverse("api:proposition", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

        self.assertFalse(
            Publication.objects.filter(
                id=self.second_index_publication_2_proposition_1.id
            ).exists()
        )

    def test_delete_proposition_forbidden(self):
        kwargs = {"id": self.second_index_publication_2_proposition_1.id}
        response = self.client.delete(
            reverse("api:proposition", kwargs=kwargs), **self.auth_user_two
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def _do_test_approve(
        self,
        approval: bool,
        proposition: Proposition,
        auth_user,
        user,
        expected_code: int,
    ):
        data = {"approved": approval}
        kwargs = {"id": proposition.id}
        response = self.client.post(
            reverse("api:proposition_approve", kwargs=kwargs),
            data=data,
            content_type="application/json",
            **auth_user
        )
        self.assertEqual(response.status_code, expected_code)

        if expected_code == HTTPStatus.OK:
            content = response.json()
            self.assertEqual(content["approved"], approval)
            self.assertEqual(content["user"]["id"], str(user.id))
            approbation = Approbation.objects.get(proposition=proposition, user=user)
            self.assertEqual(approbation.approved, approval)

    def test_approve(self):
        self._do_test_approve(
            True,
            self.second_index_publication_2_proposition_2,
            self.auth_user_one,
            self.user_one,
            HTTPStatus.OK,
        )

    def test_disapprove(self):
        self._do_test_approve(
            False,
            self.second_index_publication_2_proposition_2,
            self.auth_user_one,
            self.user_one,
            HTTPStatus.OK,
        )

    def test_approve_my_proposition(self):
        self._do_test_approve(
            True,
            self.second_index_publication_2_proposition_1,
            self.auth_user_one,
            self.user_one,
            HTTPStatus.BAD_REQUEST,
        )

    def test_get_my_approbation(self):
        Approbation.objects.create(
            proposition=self.second_index_publication_2_proposition_2,
            user=self.user_one,
            approved=True,
        )

        kwargs = {"id": self.second_index_publication_2_proposition_2.id}
        response = self.client.get(
            reverse("api:approbation", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        content = response.json()
        self.assertEqual(content["approved"], True)
        self.assertEqual(content["user"]["id"], str(self.user_one.id))

    def test_delete_my_approbation(self):
        Approbation.objects.create(
            proposition=self.second_index_publication_2_proposition_2,
            user=self.user_one,
            approved=True,
        )

        kwargs = {"id": self.second_index_publication_2_proposition_2.id}
        response = self.client.delete(
            reverse("api:approbation", kwargs=kwargs), **self.auth_user_one
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
